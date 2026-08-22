import discord
from discord import app_commands  # <-- ESSA LINHA ESTAVA FALTANDO!
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# ============ CARREGAR VARIÁVEIS DE AMBIENTE ============
load_dotenv()

# ============ CONFIGURAÇÕES DO .ENV ============
Token = os.getenv('DISCORD_TOKEN')
ChannelId = int(os.getenv('CHANNEL_ID'))
ManagerRule_ID = int(os.getenv('MANAGER_ROLE_ID'))

# ============ INTENTS ============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# ============ ARQUIVO DE DADOS ============
DATA_FILE = 'free_agency_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ============ COMANDO SLASH: /freeagent ============
@bot.tree.command(name="freeagent", description="📢 Anuncie-se como Free Agent")
@app_commands.describe(
    mensagem="Sua mensagem principal (ex: jogador versátil, experiência...)",
    experiencias="Suas experiências (ex: MR25, PRS, VEF, NBA...)",
    motivo="Motivo de estar na free agency (ex: buscando novos desafios)"
)
async def freeagent_slash(
    interaction: discord.Interaction,
    mensagem: str,
    experiencias: str,
    motivo: str
):
    """Comando slash para anunciar free agency"""
    
    # Salvar os dados do jogador
    data = load_data()
    data[str(interaction.user.id)] = {
        'experiencias': experiencias,
        'motivo': motivo,
        'mensagem': mensagem,
        'anunciado_em': str(interaction.created_at)
    }
    save_data(data)
    
    # Criar o embed
    embed = discord.Embed(
        title=f'⚡ {interaction.user.display_name} é um Free Agent!',
        description=mensagem,
        color=discord.Color.blue()
    )
    
    # ===== AVATAR CIRCULAR NA DIREITA =====
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)
    
    # ===== ADICIONAR EXPERIÊNCIAS E MOTIVO =====
    embed.add_field(
        name='🌍 **Experiências**',
        value=experiencias,
        inline=False
    )
    
    embed.add_field(
        name='💭 **Motivo da Free Agency**',
        value=motivo,
        inline=False
    )
    
    embed.add_field(
        name='👤 **Jogador**',
        value=interaction.user.mention,
        inline=True
    )
    embed.add_field(
        name='📅 **Status**',
        value='🟢 Disponível',
        inline=True
    )
    
    embed.set_footer(text='📩 Clique em "Contract" para demonstrar interesse')
    
    # ============ BOTÃO CONTRACT ============
    async def contract_callback(interact: discord.Interaction):
        if not any(role.id == int(ManagerRule_ID) for role in interact.user.roles):
            await interact.response.send_message(
                '❌ Você não tem permissão para enviar contratos!',
                ephemeral=True
            )
            return
        
        if interact.user.id == interaction.user.id:
            await interact.response.send_message(
                '❌ Você não pode enviar contrato para si mesmo!',
                ephemeral=True
            )
            return
        
        try:
            dm_embed = discord.Embed(
                title='📩 Oferta de Contrato!',
                description=f'O manager **{interact.user.display_name}** demonstrou interesse em você!',
                color=discord.Color.green()
            )
            dm_embed.add_field(
                name='💬 Mensagem do Manager',
                value=f'*"{mensagem}"*',
                inline=False
            )
            
            await interaction.user.send(embed=dm_embed)
            
            await interact.response.send_message(
                f'✅ Contrato enviado para {interaction.user.mention}!',
                ephemeral=True
            )
        except discord.Forbidden:
            await interact.response.send_message(
                '❌ O jogador tem DMs desativadas!',
                ephemeral=True
            )
    
    view = discord.ui.View()
    contract_button = discord.ui.Button(label="📩 Contract", style=discord.ButtonStyle.green)
    contract_button.callback = contract_callback
    view.add_item(contract_button)
    
    exp_button = discord.ui.Button(label="📊 Ver Experiência", style=discord.ButtonStyle.blurple)
    async def exp_callback(interact: discord.Interaction):
        exp_embed = discord.Embed(
            title=f'📊 Experiências de {interaction.user.display_name}',
            color=discord.Color.purple()
        )
        if interaction.user.avatar:
            exp_embed.set_thumbnail(url=interaction.user.avatar.url)
        exp_embed.add_field(name='🌍 **Experiências**', value=experiencias, inline=False)
        exp_embed.add_field(name='💭 **Motivo da Free Agency**', value=motivo, inline=False)
        await interact.response.send_message(embed=exp_embed, ephemeral=True)
    exp_button.callback = exp_callback
    view.add_item(exp_button)
    
    channel = bot.get_channel(int(ChannelId))
    if channel:
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f'✅ Anúncio enviado para {channel.mention}!',
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            '❌ Canal de free agency não configurado!',
            ephemeral=True
        )

# ============ SINCRONIZAR COMANDOS ============
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    print(f'📡 Em {len(bot.guilds)} servidores')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos slash sincronizados:')
        for cmd in synced:
            print(f'   • /{cmd.name}')
    except Exception as e:
        print(f'❌ Erro ao sincronizar comandos: {e}')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"/freeagent | Free Agency"
        )
    )

# ============ INICIALIZAÇÃO ============
if __name__ == '__main__':
    try:
        bot.run(Token)
    except discord.LoginFailure:
        print('❌ TOKEN INVÁLIDO!')
    except Exception as e:
        print(f'❌ ERRO FATAL: {e}')
