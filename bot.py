import discord
from discord.ext import commands
import os
# ============================================================
# CONFIGURAÇÃO
# ============================================================

TOKEN = os.getenv("TOKEN")

SERVER_ID = 1496579366677909704
FREE_AGENCY_CHANNEL_ID = 1496579368493777097

PLAYER_ROLE_ID = 1496579366698750185
MANAGER_ROLE_ID = 1496579366765723720


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()


# ============================================================
# BOT
# ============================================================

class FreeAgencyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=".",
            intents=intents
        )

    async def setup_hook(self):

        guild = discord.Object(id=SERVER_ID)

        self.tree.copy_global_to(guild=guild)

        synced = await self.tree.sync(
            guild=guild
        )

        print(
            f"[FREE AGENCY] "
            f"{len(synced)} comando(s) sincronizado(s)."
        )


bot = FreeAgencyBot()


# ============================================================
# BOT ONLINE
# ============================================================

@bot.event
async def on_ready():

    print("====================================")
    print("FREE AGENCY BOT ONLINE")
    print(f"Bot: {bot.user}")
    print(f"ID: {bot.user.id}")
    print("====================================")


# ============================================================
# FREE AGENT
# ============================================================

@bot.tree.command(
    name="freeagent",
    description="Coloca você na Free Agency"
)
@discord.app_commands.describe(
    motivo="Por que você quer entrar na Free Agency?",
    experiencia="Quais são suas experiências anteriores?",
    contratavel="Você permite que Managers te contratem?"
)
async def freeagent(
    interaction: discord.Interaction,
    motivo: str,
    experiencia: str,
    contratavel: bool
):

    # ========================================================
    # VERIFICAÇÃO DO USUÁRIO
    # ========================================================

    if not isinstance(
        interaction.user,
        discord.Member
    ):

        await interaction.response.send_message(
            "❌ Não foi possível verificar seu cargo.",
            ephemeral=True
        )

        return


    member = interaction.user


    # ========================================================
    # VERIFICAÇÃO DO PLAYER ROLE
    # ========================================================

    is_player = any(
        role.id == PLAYER_ROLE_ID
        for role in member.roles
    )


    if not is_player:

        await interaction.response.send_message(
            "❌ Apenas Players podem usar o Free Agency.",
            ephemeral=True
        )

        return


    # ========================================================
    # PROCURA O CANAL
    # ========================================================

    channel = bot.get_channel(
        FREE_AGENCY_CHANNEL_ID
    )


    if channel is None:

        await interaction.response.send_message(
            "❌ O canal da Free Agency não foi encontrado.",
            ephemeral=True
        )

        return


    # ========================================================
    # EMBED
    # ========================================================

    embed = discord.Embed(
        title=f"{member.display_name} is a Free-Agent!",
        color=discord.Color.blue()
    )


    embed.add_field(
        name="👤 Player",
        value=member.mention,
        inline=False
    )


    embed.add_field(
        name="💭 Why do they want Free Agency?",
        value=motivo,
        inline=False
    )


    embed.add_field(
        name="⚽ Experience",
        value=experiencia,
        inline=False
    )


    if contratavel:

        embed.add_field(
            name="📄 Contract Status",
            value="✅ Available for contracts",
            inline=False
        )

    else:

        embed.add_field(
            name="📄 Contract Status",
            value="🔒 Not available for contracts",
            inline=False
        )


    if member.avatar:

        embed.set_thumbnail(
            url=member.avatar.url
        )


    embed.set_footer(
        text="Free Agency"
    )


    # ========================================================
    # VIEW
    # ========================================================

    view = discord.ui.View(
        timeout=None
    )


    # ========================================================
    # CONTRACT BUTTON
    # ========================================================

    button = discord.ui.Button(
        label="Contract",
        style=discord.ButtonStyle.green,
        disabled=not contratavel
    )


    # ========================================================
    # CONTRACT CALLBACK
    # ========================================================

    async def contract_callback(
        button_interaction: discord.Interaction
    ):

        # ----------------------------------------------------
        # VERIFICA MANAGER
        # ----------------------------------------------------

        if not isinstance(
            button_interaction.user,
            discord.Member
        ):

            await button_interaction.response.send_message(
                "❌ Não foi possível verificar seu cargo.",
                ephemeral=True
            )

            return


        manager = button_interaction.user


        is_manager = any(
            role.id == MANAGER_ROLE_ID
            for role in manager.roles
        )


        if not is_manager:

            await button_interaction.response.send_message(
                "❌ Apenas Managers podem contratar Players.",
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # PLAYER JÁ NÃO ESTÁ MAIS DISPONÍVEL?
        # ----------------------------------------------------

        if not contratavel:

            await button_interaction.response.send_message(
                "❌ Este Player não está disponível para contratação.",
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # MANAGER CONTRATOU
        # ----------------------------------------------------

        await button_interaction.response.send_message(
            f"✅ {manager.mention} contratou "
            f"{member.mention}!"
        )


        # ----------------------------------------------------
        # DM PARA O PLAYER
        # ----------------------------------------------------

        try:

            await member.send(
                f"🎉 **You have been contracted!**\n\n"
                f"**Manager:** {manager.display_name}\n"
                f"**Server:** {interaction.guild.name}\n\n"
                f"Congratulations!"
            )

        except discord.Forbidden:

            print(
                f"[WARNING] "
                f"Não foi possível enviar DM para "
                f"{member}."
            )


        # ----------------------------------------------------
        # DESABILITA O BOTÃO
        # ----------------------------------------------------

        button.disabled = True

        try:

            await button_interaction.message.edit(
                view=view
            )

        except discord.NotFound:

            pass


    button.callback = contract_callback

    view.add_item(button)


    # ========================================================
    # ENVIA NO CANAL
    # ========================================================

    await channel.send(
        embed=embed,
        view=view
    )


    # ========================================================
    # CONFIRMAÇÃO
    # ========================================================

    await interaction.response.send_message(
        "✅ Seu perfil foi colocado na Free Agency!",
        ephemeral=True
    )


# ============================================================
# START
# ============================================================

bot.run(TOKEN)
