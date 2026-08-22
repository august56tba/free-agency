import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# ============ CARREGAR VARIÁVEIS ============
load_dotenv()

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

# ============ COMANDO PARA REGISTRAR EXPERIÊNCIA ============
@bot.command(name='setexp')
async def set_experience(ctx):
    """Registra suas experiências"""
    
    class ExpModal(discord.ui.Modal, title='📝 Minhas Experiências'):
        experiencias = discord.ui.TextInput(
            label='🌍 Experiências (ligas/equipes)',
            placeholder='Ex: MR25, PRS, VEF Riga, NBA 2024',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        motivo = discord.ui.TextInput(
            label='💭 Motivo da Free Agency',
            placeholder='Ex: Buscando novos desafios',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=300
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            data = load_data()
            data[str(interaction.user.id)] = {
                'experiencias': self.experiencias.value,
                'motivo': self.motivo.value
            }
            save_data(data)
            
            embed = discord.Embed(
                title='✅ Experiência Registrada!',
                description=f'{interaction.user.mention}, suas experiências foram salvas!',
                color=discord.Color.green()
            )
            embed.add_field(name='🌍 Experiências', value=self.experiencias.value, inline=False)
            embed.add_field(name='💭 Motivo', value=self.motivo.value, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await ctx.send_modal(ExpModal())

# ============ COMANDO FREEAGENT ============
@bot.command(name='freeagent')
async def freeagent(ctx, *, mensagem: str = "Sem mensagem adicional"):
    """Anuncia na free agency"""
    
    data = load_data()
    player_data = data.get(str(ctx.author.id))
    
    embed = discord.Embed(
        title=f'⚡ {ctx.author.display_name} é um Free Agent!',
        description=mensagem,
        color=discord.Color.blue()
    )
    
    # Avatar na direita
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    
    # Mostrar experiências se tiver
    if player_data:
        embed.add_field(
            name='🌍 **Experiências**',
            value=player_data.get('experiencias', '*Nenhuma*'),
            inline=False
        )
        embed.add_field(
            name='💭 **Motivo**',
            value=player_data.get('motivo', '*Não informado*'),
            inline=False
        )
    else:
        embed.add_field(
            name='⚠️ **Aviso**',
            value='Use `.setexp` para registrar suas experiências!',
            inline=False
        )
    
    embed.add_field(name='👤 **Jogador**', value=ctx.author.mention, inline=True)
    embed.add_field(name='📅 **Status**', value='🟢 Disponível', inline=True)
    
    # ============ BOTÃO CONTRACT ============
    async def contract_callback(interact: discord.Interaction):
        if not any(role.id == ManagerRule_ID for role in interact.user.roles):
            await interact.response.send_message('❌ Sem permissão!', ephemeral=True)
            return
        
        if interact.user.id == ctx.author.id:
            await interact.response.send_message('❌ Não pode contratar a si mesmo!', ephemeral=True)
            return
        
        try:
            await ctx.author.send(f'📩 Contrato de {interact.user.display_name}!\n💬 {mensagem}')
            await interact.response.send_message(f'✅ Contrato enviado!', ephemeral=True)
        except:
            await interact.response.send_message('❌ DMs desativadas!', ephemeral=True)
    
    view = discord.ui.View()
    button = discord.ui.Button(label="📩 Contract", style=discord.ButtonStyle.green)
    button.callback = contract_callback
    view.add_item(button)
    
    # Botão Ver Experiência
    exp_button = discord.ui.Button(label="📊 Ver Exp", style=discord.ButtonStyle.blurple)
    async def exp_callback(interact: discord.Interaction):
        exp_embed = discord.Embed(
            title=f'📊 {ctx.author.display_name}',
            color=discord.Color.purple()
        )
        if ctx.author.avatar:
            exp_embed.set_thumbnail(url=ctx.author.avatar.url)
        
        if player_data:
            exp_embed.add_field(name='🌍 Experiências', value=player_data.get('experiencias', '*Nenhuma*'), inline=False)
            exp_embed.add_field(name='💭 Motivo', value=player_data.get('motivo', '*Não informado*'), inline=False)
        else:
            exp_embed.description = '❌ Sem experiências registradas'
        
        await interact.response.send_message(embed=exp_embed, ephemeral=True)
    exp_button.callback = exp_callback
    view.add_item(exp_button)
    
    channel = bot.get_channel(ChannelId)
    if channel:
        await channel.send(embed=embed, view=view)
        await ctx.send(f'✅ Anunciado em {channel.mention}!')
    else:
        await ctx.send(embed=embed, view=view)

# ============ COMANDO VER EXPERIÊNCIA ============
@bot.command(name='exp')
async def view_exp(ctx, member: discord.Member = None):
    target = member or ctx.author
    data = load_data()
    player_data = data.get(str(target.id))
    
    embed = discord.Embed(
        title=f'📊 {target.display_name}',
        color=discord.Color.blue()
    )
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)
    
    if player_data:
        embed.add_field(name='🌍 Experiências', value=player_data.get('experiencias', '*Nenhuma*'), inline=False)
        embed.add_field(name='💭 Motivo', value=player_data.get('motivo', '*Não informado*'), inline=False)
    else:
        embed.description = '❌ Nenhuma experiência registrada'
    
    await ctx.send(embed=embed)

# ============ EVENTO READY ============
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    print(f'📡 Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=".freeagent | Free Agency"))

# ============ INICIALIZAR ============
if __name__ == '__main__':
    try:
        bot.run(Token)
    except Exception as e:
        print(f'❌ ERRO: {e}')
