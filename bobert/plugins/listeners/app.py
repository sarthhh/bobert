from datetime import datetime

import hikari
import lightbulb
import miru

from bobert.core.utils import helpers
from bobert.core.utils.helpers import (
    get_acceptance_message,
    get_questions,
    get_rejection_message,
)

app = lightbulb.Plugin("app")

"""
TODO:
- Add database so users cannot submit multiple forms
"""


class AppButton(miru.View):
    @miru.button(
        label="Approve", style=hikari.ButtonStyle.SUCCESS, custom_id="approve_button"
    )
    async def approve_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        try:
            print("Approve button clicked")

            # Extract target user ID from the footer
            footer_text = (
                ctx.interaction.message.embeds[0].footer.text
                if ctx.interaction.message.embeds[0].footer
                else None
            )
            if footer_text and "UID: " in footer_text:
                user_id = int(footer_text.split("UID: ")[1])
                target = app.bot.cache.get_user(user_id)
            else:
                target = None
            print(f"Target user: {target}")

            # Extract role from the author name
            author_name = (
                ctx.interaction.message.embeds[0].author.name
                if ctx.interaction.message.embeds[0].author
                else None
            )
            role = author_name.split(" Application -")[0] if author_name else None
            print(f"Role: {role}")

            if not target:
                await ctx.respond("User not found.", flags=hikari.MessageFlag.EPHEMERAL)
                return

            if role is None:
                await ctx.respond(
                    "Role not specified.", flags=hikari.MessageFlag.EPHEMERAL
                )
                return

            message = get_acceptance_message(role)
            print(f"Acceptance message: {message}")

            if message:
                embed = hikari.Embed(
                    title=message["title"],
                    description=message["description"].format(user=target),
                    color=0xFFFFFF,
                )
                for field in message["fields"]:
                    embed.add_field(
                        name=field["name"], value=field["value"], inline=False
                    )

                embed.set_author(name="🔔 Important Notice")
                await target.send(embed=embed)

            existing_embed = ctx.interaction.message.embeds[0]
            existing_embed.set_thumbnail(
                "https://cdn.discordapp.com/emojis/1059009032876199976.png"
            )

            view = miru.View()
            view.add_item(
                miru.Button(
                    label="Application Approved",
                    style=hikari.ButtonStyle.SUCCESS,
                    disabled=True,
                )
            )
            await ctx.edit_response(embeds=[existing_embed], components=view)
        except Exception as e:
            print(f"Error in approve_button: {str(e)}")
            await ctx.respond(
                f"An error occurred: `{str(e)}`", flags=hikari.MessageFlag.EPHEMERAL
            )

    @miru.button(
        label="Reject", style=hikari.ButtonStyle.DANGER, custom_id="reject_button"
    )
    async def reject_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        try:
            print("Reject button clicked")

            # Extract target user ID from the footer
            footer_text = (
                ctx.interaction.message.embeds[0].footer.text
                if ctx.interaction.message.embeds[0].footer
                else None
            )
            if footer_text and "UID: " in footer_text:
                user_id = int(footer_text.split("UID: ")[1])
                target = app.bot.cache.get_user(user_id)
            else:
                target = None
            print(f"Target user: {target}")

            # Extract role from the author name
            author_name = (
                ctx.interaction.message.embeds[0].author.name
                if ctx.interaction.message.embeds[0].author
                else None
            )
            role = author_name.split(" Application -")[0] if author_name else None
            print(f"Role: {role}")

            if not target:
                await ctx.respond("User not found.", flags=hikari.MessageFlag.EPHEMERAL)
                return

            if role is None:
                await ctx.respond(
                    "Role not specified.", flags=hikari.MessageFlag.EPHEMERAL
                )
                return

            message = get_rejection_message(role)
            print(f"Rejection message: {message}")

            if message:
                embed = hikari.Embed(
                    title=message["title"],
                    description=message["description"].format(user=target),
                    color=0xFFFFFF,
                )
                for field in message["fields"]:
                    embed.add_field(
                        name=field["name"], value=field["value"], inline=False
                    )

                embed.set_author(name="🔔 Important Notice")
                await target.send(embed=embed)

            existing_embed = ctx.interaction.message.embeds[0]
            existing_embed.set_thumbnail(
                "https://cdn.discordapp.com/emojis/1059009054044864532.png"
            )

            view = miru.View()
            view.add_item(
                miru.Button(
                    label="Application Rejected",
                    style=hikari.ButtonStyle.DANGER,
                    disabled=True,
                )
            )
            await ctx.edit_response(embeds=[existing_embed], components=view)
        except Exception as e:
            print(f"Error in reject_button: {str(e)}")
            await ctx.respond(
                f"An error occurred: `{str(e)}`", flags=hikari.MessageFlag.EPHEMERAL
            )


class AppModal(miru.Modal):
    def __init__(self, role: str) -> None:
        self.role = role
        title = f"{role} Application Form"
        super().__init__(title=title)
        print(f"Creating modal for role: {role}")

        self.questions = get_questions(role)
        self.inputs = {}

        for question, placeholder in self.questions:
            input_text = miru.TextInput(
                label=question,
                placeholder=placeholder,
                style=hikari.TextInputStyle.PARAGRAPH,
            )
            self.inputs[question] = input_text
            self.add_item(input_text)

    async def callback(self, ctx: miru.ModalContext) -> None:
        print("Modal callback triggered")
        view = AppButton()
        target = ctx.member

        color = None
        if target:
            roles = helpers.sort_roles(target.get_roles())
            c = [r.color for r in roles if r.color]
            color = c[0] if c else None
        print(f"User color: {color}")

        embed = hikari.Embed(
            color=color,
            timestamp=datetime.now().astimezone(),
        )

        for question, input_text in self.inputs.items():
            embed.add_field(
                name=question,
                value=input_text.value,
                inline=False,
            )
            print(f"Question: {question}, Answer: {input_text.value}")

        embed.set_author(
            name=f"{self.role} Application - {str(target)}",
            icon=target.display_avatar_url if target else None,
        )
        embed.set_footer(text=f"UID: {target.id if target else 'Unknown ID'}")

        print(f"Sending application embed for {target}")

        await app.bot.rest.create_message(
            1044066400068710473, embed=embed, components=view  # test server channel ID
        )

        await ctx.respond(
            "Your application was submitted successfully!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


class AppRoles(miru.View):
    @miru.text_select(
        placeholder="Select a position...",
        options=[
            miru.SelectOption(label="Event Host"),
            miru.SelectOption(label="Event Assistant"),
            miru.SelectOption(label="Trainee"),
        ],
        custom_id="app_roles",
    )
    async def app_button(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
        print(f"Select menu triggered with value: {select.values}")
        role = select.values[0]
        print(f"Selected role: {role}")
        await ctx.respond_with_modal(AppModal(role))


@app.listener(hikari.StartedEvent)
async def start_button(event: hikari.StartedEvent) -> None:
    view = AppRoles(timeout=None)
    app.bot.d.miru.start_view(view)

    view1 = AppButton(timeout=None)
    app.bot.d.miru.start_view(view1, bind_to=None)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(app)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(app)
