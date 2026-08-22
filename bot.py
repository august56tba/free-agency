import discord
from discord.ext import commands
import json
import os

# ============ CONFIGURAÇÕES ============
Token = 'SEU_TOKEN_AQUI'
ChannelId = 1496579368493777097  # ID do canal
Admin_ID = 1496579366765723725
ManagerRule_ID = 1496579366765723720

# ============ INTENTS ============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# ============ SISTEMA DE ARMAZENAMENTO DAS EXPERIÊNCIAS ============
EXPERIENCE_FILE = 'player_experiences.json'

def load_experiences():
    """Carrega as experiências salvas dos jogadores"""
    if os.path.exists(EXPERIENCE_FILE):
        with open(EXPERIENCE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_experiences(data):
    """Salva as experiências dos jogadores"""
    with open(EXPERIENCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_player_exp(user_id):
    """Retorna a experiência de um jogador"""
    data = load_experiences()
    return data.get(str(user_id), {})

def set_player_exp(user_id, exp_text, reason_text):
    """Define a experiência e motivo do jogador"""
    data = load_experiences()
    data[str(user_id)] = {
        'experience': exp_text,
        'reason': reason_text
    }
    save_experiences(data)

# ============ COMANDO PARA DEFINIR EXPERIÊNCIA ============
@bot.command(name='setexp')
async def set_experience(ctx):
    """Abre um modal para definir suas experiências"""
    
    class ExperienceModal(discord.ui.Modal, title=' Minhas Experiências'):
        experience = discord.ui.TextInput(
            label='🌍 Experiências / Ligas que jogou',
            placeholder='Ex: VEF, PRS, Maracanã25, NBA, EuroLeague...',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        reason = discord.ui.TextInput(
            label='💭 Por que está na Free Agency?',
            placeholder='Ex: Buscando novos desafios, time acabou...',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=300
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            # Salvar a experiência do jogador
            set_player_exp(
                interaction.user.id,
                self.experience.value,
                self.reason.value
            )
            
            embed = discord.Embed(
                title='✅ Experiência Registrada!',
                description=f'{interaction.user.mention}, suas experiências foram salvas com sucesso!',
                color=discord.Color.green()
            )
            embed.add_field(
                name='🌍 Experiências',
                value=self.experience.value,
                inline=False
            )
            embed.add_field(
                name='💭 Motivo',
                value=self.reason.value,
                inline=False
            )
            embed.set_footer(text='Use .freeagent para anunciar!')
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await ctx.send_modal(ExperienceModal())

# ============ COMANDO PRINCIPAL FREEAGENT ============
@bot.command(name='freeagent', aliases=['FreeAgents', 'FreeAgent'])
async def freeagent(ctx, *, content: str = "No additional information provided"):
    """Anuncia um jogador como Free Agent com suas experiências"""
    
    # Pegar as experiências do jogador
    player_exp = get_player_exp(ctx.author.id)
    
    # Criar o embed
    embed = discord.Embed(
        title=f'⚡ {ctx.author.display_name} é um Free Agent!',
        description=content,
        color=discord.Color.blue()
    )
    
    # ===== AVATAR CIRCULAR NA DIREITA =====
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    
    # ===== ADICIONAR EXPERIÊNCIAS E MOTIVO =====
    if player_exp:
        # Campo de Experiências
        embed.add_field(
            name='🌍 **Experiências**',
            value=player_exp.get('experience', '*Nenhuma experiência registrada*'),
            inline=False
        )
        
        # Campo do Motivo
        embed.add_field(
            name='💭 **Motivo da Free Agency**',
            value=player_exp.get('reason', '*Motivo não informado*'),
            inline=False
        )
    else:
        embed.add_field(
            name='⚠️ **Experiências**',
            value='*Jogador ainda não registrou suas experiências*\nUse `.setexp` para adicionar!',
            inline=False
        )
    
    # Informações adicionais
    embed.add_field(
        name='👤 **Jogador**',
        value=ctx.author.mention,
        inline=True
    )
    embed.add_field(
        name='📅 **Status**',
        value='🟢 Disponível',
        inline=True
    )
    
    embed.set_footer(text='📩 Clique em "Contract"')
    
    # ============ BOTÃO CONTRACT ============
    async def contract_callback(interact: discord.Interaction):
        """Callback do botão Contract"""
        # Verificar se é manager
        if not any(role.id == int(ManagerRule_ID) for role in interact.user.roles):
            await interact.response.send_message(
                '❌ Você não tem permissão para enviar contratos!',
                ephemeral=True
            )
            return
        
        # Verificar se não é o próprio jogador
        if interact.user.id == ctx.author.id:
            await interact.response.send_message(
                '❌ Você não pode enviar contrato para si mesmo!',
                ephemeral=True
            )
            return
        
        # Enviar mensagem pro jogador
        try:
            await ctx.author.send(
                f"📩 **Oferta de Contrato!**\n"
                f"O manager **{interact.user.display_name}** demonstrou interesse em você!\n"
                f"💬 Mensagem do manager: *{content}*"
            )
            
            await interact.response.send_message(
                f'✅ Contrato enviado para {ctx.author.mention}!',
                ephemeral=True
            )
        except discord.Forbidden:
            await interact.response.send_message(
                '❌ O jogador tem DMs desativadas!',
                ephemeral=True
            )
    
    # Criar view
    view = discord.ui.View()
    
    # Botão Contract
    contract_button = discord.ui.Button(
        label="📩 Contract",
        style=discord.ButtonStyle.green
    )
    contract_button.callback = contract_callback
    
    # Desabilitar se não for manager
    if not any(role.id == int(ManagerRule_ID) for role in ctx.author.roles):
        contract_button.disabled = True
        contract_button.label = "🔒 Apenas Managers"
    
    view.add_item(contract_button)
    
    # ===== BOTÃO PARA VER EXPERIÊNCIA (OPCIONAL) =====
    exp_button = discord.ui.Button(
        label="📊 Ver Experiência",
        style=discord.ButtonStyle.blurple
    )
    
    async def exp_callback(interact: discord.Interaction):
        """Mostra a experiência do jogador"""
        exp_data = get_player_exp(ctx.author.id)
        
        exp_embed = discord.Embed(
            title=f'📊 Experiências de {ctx.author.display_name}',
            color=discord.Color.purple()
        )
        
        if ctx.author.avatar:
            exp_embed.set_thumbnail(url=ctx.author.avatar.url)
        
        if exp_data:
            exp_embed.add_field(
                name='🌍 **Experiências**',
                value=exp_data.get('experience', '*Nenhuma*'),
                inline=False
            )
            exp_embed.add_field(
                name='💭 **Motivo**',
                value=exp_data.get('reason', '*Não informado*'),
                inline=False
            )
        else:
            exp_embed.description = '❌ Jogador não registrou experiências ainda.'
        
        await interact.response.send_message(embed=exp_embed, ephemeral=True)
    
    exp_button.callback = exp_callback
    view.add_item(exp_button)
    
    # Enviar mensagem
    channel = bot.get_channel(int(ChannelId))
    if channel:
        await channel.send(embed=embed, view=view)
        await ctx.send(f'✅ Anúncio enviado para {channel.mention}!')
    else:
        await ctx.send(embed=embed, view=view)

# ============ COMANDO PARA VER EXPERIÊNCIA ============
@bot.command(name='experience', aliases=['exp', 'myexp'])
async def view_experience(ctx, member: discord.Member = None):
    """Vê as experiências de um jogador"""
    target = member or ctx.author
    exp_data = get_player_exp(target.id)
    
    embed = discord.Embed(
        title=f'📊 Experiências de {target.display_name}',
        color=discord.Color.blue()
    )
    
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)
    
    if exp_data:
        embed.add_field(
            name=' **Experiências**',
            value=exp_data.get('experience', '*Nenhuma experiência registrada*'),
            inline=False
        )
        embed.add_field(
            name=' **Free Agency**',
            value=exp_data.get('reason', '*Motivo não informado*'),
            inline=False
        )
    else:
        embed.description = '❌ Este jogador ainda não registrou suas experiências.\nUse `.setexp` para adicionar!'
    
    await ctx.send(embed=embed)

# ============ COMANDO ADMIN PARA EDITAR EXP DE ALGUÉM ============
@bot.command(name='editexp')
@commands.has_permissions(administrator=True)
async def edit_experience(ctx, member: discord.Member):
    """Edita a experiência de um jogador (Admin)"""
    
    class AdminExpModal(discord.ui.Modal, title='✏️ Editar Experiência'):
        experience = discord.ui.TextInput(
            label='🌍 Experiências',
            placeholder='VEF, PRS, Maracanã25...',
            style=discord.TextStyle.paragraph,
            required=True
        )
        
        reason = discord.ui.TextInput(
            label='💭 Motivo',
            placeholder='Buscando novos desafios...',
            style=discord.TextStyle.paragraph,
            required=True
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            set_player_exp(member.id, self.experience.value, self.reason.value)
            await interaction.response.send_message(
                f'✅ Experiências de {member.mention} atualizadas!',
                ephemeral=True
            )
    
    await ctx.send_modal(AdminExpModal())

# ============ COMANDO ADMIN PARA REMOVER EXP ============
@bot.command(name='removexp')
@commands.has_permissions(administrator=True)
async def remove_experience(ctx, member: discord.Member):
    """Remove as experiências de um jogador (Admin)"""
    data = load_experiences()
    if str(member.id) in data:
        del data[str(member.id)]
        save_experiences(data)
        await ctx.send(f'🗑️ Experiências de {member.mention} removidas!')
    else:
        await ctx.send(f'❌ {member.mention} não tem experiências registradas.')

# ============ EVENTO DE READY ============
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    print(f'📡 Em {len(bot.guilds)} servidores')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"Free Agency | .freeagent"
        )
    )

# ============ TRATAMENTO DE ERROS ============
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ Você não tem permissão para isso!')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('❌ Membro não encontrado!')
    else:
        print(f'Erro: {error}')
        await ctx.send('❌ Ocorreu um erro. Tente novamente.')

# ============ INICIALIZAÇÃO ============
if __name__ == '__main__':
    try:
        bot.run(Token)
    except discord.LoginFailure:
        print('❌ TOKEN INVÁLIDO!')
    except Exception as e:
        print(f'❌ ERRO: {e}')
