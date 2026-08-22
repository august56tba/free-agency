import discord
from discord.ext import commands
import json
import os

# ============ CONFIGURAÇÕES ============
Token = 'SEU_TOKEN_AQUI'
ChannelId = 1496579368493777097  # ID do canal
ManagerRule_ID = 1496579366765723720

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
@bot.tree.command(name="freeagent", description=" Anuncie-se como Free Agent")
@app_commands.describe(
    mensagem="Sua mensagem principal (ex: jogador versátil, experiência...)",
    experiencias="Suas experiências (ex: MII MASSINHA, PRS, VEF, NBA...)",
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
        title=f' {interaction.user.display_name} é um Free Agent!',
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
        name=' **Jogador**',
        value=interaction.user.mention,
        inline=True
    )
    embed.add_field(
        name='📅 **Status**',
        value='🟢 Disponível',
        inline=True
    )
    embed.add_field(
        name='📌 **Anunciado em**',
        value=interaction.created_at.strftime('%d/%m/%Y às %H:%M'),
        inline=True
    )
    
    embed.set_footer(text='📩 Clique em "Contract" para demonstrar interesse')
    
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
        if interact.user.id == interaction.user.id:
            await interact.response.send_message(
                '❌ Você não pode enviar contrato para si mesmo!',
                ephemeral=True
            )
            return
        
        # Enviar mensagem pro jogador
        try:
            # DM para o jogador
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
            dm_embed.add_field(
                name='📊 Experiências do Jogador',
                value=experiencias,
                inline=False
            )
            dm_embed.set_footer(text=f'Interação no servidor {interact.guild.name}')
            
            await interaction.user.send(embed=dm_embed)
            
            await interact.response.send_message(
                f'✅ Contrato enviado para {interaction.user.mention}!',
                ephemeral=True
            )
        except discord.Forbidden:
            await interact.response.send_message(
                '❌ O jogador tem DMs desativadas! Não foi possível enviar a mensagem.',
                ephemeral=True
            )
    
    # Criar view com botões
    view = discord.ui.View()
    
    # Botão Contract
    contract_button = discord.ui.Button(
        label="📩 Contract",
        style=discord.ButtonStyle.green
    )
    contract_button.callback = contract_callback
    view.add_item(contract_button)
    
    # Botão Ver Experiência
    exp_button = discord.ui.Button(
        label="📊 Ver Experiência",
        style=discord.ButtonStyle.blurple
    )
    
    async def exp_callback(interact: discord.Interaction):
        """Mostra a experiência completa do jogador"""
        exp_embed = discord.Embed(
            title=f'📊 Experiências de {interaction.user.display_name}',
            color=discord.Color.purple()
        )
        
        if interaction.user.avatar:
            exp_embed.set_thumbnail(url=interaction.user.avatar.url)
        
        exp_embed.add_field(
            name=' **Experiências**',
            value=experiencias,
            inline=False
        )
        exp_embed.add_field(
            name='💭 **Free Agency**',
            value=motivo,
            inline=False
        )
        exp_embed.add_field(
            name='📌 **Anunciado em**',
            value=interaction.created_at.strftime('%d/%m/%Y às %H:%M'),
            inline=False
        )
        
        await interact.response.send_message(embed=exp_embed, ephemeral=True)
    
    exp_button.callback = exp_callback
    view.add_item(exp_button)
    
    # ===== ADICIONAR BOTÃO DE AVALIAÇÃO =====
    rate_button = discord.ui.Button(
        label="⭐ Avaliar Jogador",
        style=discord.ButtonStyle.gray,
        emoji="⭐"
    )
    
    async def rate_callback(interact: discord.Interaction):
        """Abre modal para avaliar o jogador"""
        
        class RatingModal(discord.ui.Modal, title='⭐ Avaliar Jogador'):
            rating = discord.ui.TextInput(
                label='Nota (1-5)',
                placeholder='Digite um número de 1 a 5',
                required=True,
                max_length=1
            )
            
            comment = discord.ui.TextInput(
                label='Comentário',
                placeholder='Sua opinião sobre o jogador...',
                style=discord.TextStyle.paragraph,
                required=False,
                max_length=200
            )
            
            async def on_submit(self, modal_interact: discord.Interaction):
                try:
                    nota = int(self.rating.value)
                    if nota < 1 or nota > 5:
                        await modal_interact.response.send_message(
                            '❌ Nota deve ser entre 1 e 5!',
                            ephemeral=True
                        )
                        return
                    
                    # Salvar avaliação
                    data = load_data()
                    player_id = str(interaction.user.id)
                    if player_id not in data:
                        data[player_id] = {}
                    if 'avaliacoes' not in data[player_id]:
                        data[player_id]['avaliacoes'] = []
                    
                    data[player_id]['avaliacoes'].append({
                        'avaliador': str(modal_interact.user.id),
                        'avaliador_nome': modal_interact.user.display_name,
                        'nota': nota,
                        'comentario': self.comment.value or 'Sem comentário',
                        'data': str(modal_interact.created_at)
                    })
                    save_data(data)
                    
                    # Calcular média
                    avaliacoes = data[player_id]['avaliacoes']
                    media = sum(a['nota'] for a in avaliacoes) / len(avaliacoes)
                    
                    await modal_interact.response.send_message(
                        f'✅ Avaliação registrada! Média atual: {media:.1f}⭐',
                        ephemeral=True
                    )
                except ValueError:
                    await modal_interact.response.send_message(
                        '❌ Digite um número válido!',
                        ephemeral=True
                    )
        
        await interact.response.send_modal(RatingModal())
    
    rate_button.callback = rate_callback
    view.add_item(rate_button)
    
    # Enviar mensagem no canal
    channel = bot.get_channel(int(ChannelId))
    if channel:
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f'✅ Anúncio enviado para {channel.mention}!',
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            '❌ Canal de free agency não configurado corretamente!',
            ephemeral=True
        )

# ============ COMANDO SLASH: /myprofile ============
@bot.tree.command(name="myprofile", description="👤 Ver seu perfil de Free Agent")
async def myprofile_slash(interaction: discord.Interaction):
    """Mostra o perfil do jogador"""
    data = load_data()
    player_data = data.get(str(interaction.user.id))
    
    if not player_data:
        await interaction.response.send_message(
            '❌ Você ainda não anunciou como Free Agent!\nUse `/freeagent` para se anunciar.',
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f'👤 Perfil de {interaction.user.display_name}',
        color=discord.Color.gold()
    )
    
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)
    
    embed.add_field(
        name='🌍 **Experiências**',
        value=player_data.get('experiencias', '*Não registrado*'),
        inline=False
    )
    
    embed.add_field(
        name='💭 **Motivo**',
        value=player_data.get('motivo', '*Não registrado*'),
        inline=False
    )
    
    embed.add_field(
        name='📌 **Anunciado em**',
        value=player_data.get('anunciado_em', '*Data não disponível*'),
        inline=False
    )
    
    # Mostrar avaliações se tiver
    if 'avaliacoes' in player_data and player_data['avaliacoes']:
        avaliacoes = player_data['avaliacoes']
        media = sum(a['nota'] for a in avaliacoes) / len(avaliacoes)
        
        embed.add_field(
            name='⭐ Avaliações',
            value=f'Média: {media:.1f}⭐ ({len(avaliacoes)} avaliações)',
            inline=False
        )
        
        # Últimas 3 avaliações
        ultimas = avaliacoes[-3:]
        for av in ultimas:
            embed.add_field(
                name=f'⭐ {av["nota"]}⭐ por {av["avaliador_nome"]}',
                value=f'💬 {av["comentario"]}',
                inline=False
            )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============ COMANDO SLASH: /search ============
@bot.tree.command(name="search", description="🔍 Buscar Free Agents")
@app_commands.describe(
    termo="Termo para buscar (nome, experiência, etc)"
)
async def search_slash(interaction: discord.Interaction, termo: str):
    """Busca por free agents"""
    data = load_data()
    
    if not data:
        await interaction.response.send_message(
            '📭 Nenhum jogador cadastrado na free agency.',
            ephemeral=True
        )
        return
    
    resultados = []
    for user_id, player_data in data.items():
        try:
            user = await bot.fetch_user(int(user_id))
            # Buscar nos campos
            if (termo.lower() in user.display_name.lower() or
                termo.lower() in player_data.get('experiencias', '').lower() or
                termo.lower() in player_data.get('motivo', '').lower() or
                termo.lower() in player_data.get('mensagem', '').lower()):
                resultados.append((user, player_data))
        except:
            continue
    
    if not resultados:
        await interaction.response.send_message(
            f'🔍 Nenhum jogador encontrado para "{termo}".',
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f'🔍 Resultados para "{termo}"',
        description=f'Encontrado(s) {len(resultados)} jogador(es)',
        color=discord.Color.blue()
    )
    
    for user, data in resultados[:10]:
        embed.add_field(
            name=f'⚡ {user.display_name}',
            value=f'🌍 {data.get("experiencias", "Sem exp")[:50]}...\n💭 {data.get("motivo", "Sem motivo")[:50]}...',
            inline=False
        )
    
    if len(resultados) > 10:
        embed.set_footer(text=f'Mostrando 10 de {len(resultados)} resultados')
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============ SINCRONIZAR COMANDOS ============
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    print(f'📡 Em {len(bot.guilds)} servidores')
    
    # Sincronizar slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos slash sincronizados:')
        for cmd in synced:
            print(f'   • /{cmd.name}')
    except Exception as e:
        print(f'❌ Erro ao sincronizar comandos: {e}')
    
    # Atualizar status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"/freeagent | Free Agency"
        )
    )

# ============ TRATAMENTO DE ERROS ============
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Comando não encontrado. Use slash commands: `/`')
    else:
        print(f'Erro: {error}')

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            '❌ Você não tem permissão para usar este comando!',
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f'❌ Erro: {error}',
            ephemeral=True
        )

# ============ INICIALIZAÇÃO ============
if __name__ == '__main__':
    try:
        bot.run(Token)
    except discord.LoginFailure:
        print('❌ TOKEN INVÁLIDO! Verifique seu token.')
    except Exception as e:
        print(f'❌ ERRO FATAL: {e}')
