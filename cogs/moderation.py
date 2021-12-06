# This Code Is Under The MPL-2.0 License
import nextcord
import random
import asyncio
import json
from nextcord.colour import Color
from nextcord.components import Button
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ext.commands.cooldowns import BucketType
from nextcord.ui.view import View
from nextcord.ext import commands
from global_functions import (
    ban_msg,
    kick_msg,
    BOT_USER_ID,
    read_database,
    write_database,
    PREFIX,
)
from difflib import get_close_matches
from ..internal.cog import Cog


class BanConfirm(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(
        label="Confirm", style=nextcord.ButtonStyle.green, custom_id="yes"
    )
    async def confirm(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red, custom_id="no")
    async def cancel(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        self.value = False
        self.stop()


class LockConfirm(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(
        label="Confirm", style=nextcord.ButtonStyle.green, custom_id="yes"
    )
    async def confirm(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red, custom_id="no")
    async def cancel(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        self.value = False
        self.stop()


class Moderation(Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.author.id) != str(BOT_USER_ID):
            send = message.channel.send

    @commands.command(name="ban", description="Bans the member from your server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, Context, member: nextcord.Member = None, *, reason=None):
        if member == None:
            embed1 = nextcord.Embed(
                title="Ban Error", description="Member to ban - Not Found"
            )
            return await Context.send(embed=embed1)
        if member.id == Context.author.id:
            embed69 = nextcord.Embed(
                title="Ban Error",
                description="Can not ban yourself, trust me I woulda ages ago <:hehe:796743161208504320>",
            )
            return await Context.send(embed=embed69)
        elif Context.author.top_role.position < member.top_role.position:
            em3 = nextcord.Embed(
                title="Ban Error",
                description="Member **higher** than you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        elif Context.author.top_role.position == member.top_role.position:
            em3 = nextcord.Embed(
                title="Ban Error",
                description="Member has same role as you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        guild = Context.guild
        banMsg = random.choice(ban_msg)
        banEmbed = nextcord.Embed(
            title="Ban Success", description=f"{member.mention} {banMsg}"
        )
        banEmbed.add_field(name="Reason", value=reason)
        await Context.send(embed=banEmbed)
        await member.send(f"You got banned in **{guild}** | Reason: **{reason}**")
        await member.ban(reason=reason)

    @commands.command(description="Unbans a member from your server by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, Context, id: int):
        user = await self.Bot.fetch_user(id)
        await Context.guild.unban(user)
        em = nextcord.Embed(title="Unban Success", description="Unbanned user :D")
        await Context.send(embed=em)

    @commands.command(name="kick", description="Kicks the member from your server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, Context, member: nextcord.Member = None, *, reason=None):
        if member == None:
            embed1 = nextcord.Embed(
                title="Kick Error", description="Member to kick - Not Found"
            )
            return await Context.send(embed=embed1)
        if not (Context.guild.me.guild_permissions.kick_members):
            embed2 = nextcord.Embed(
                title="Kick Error",
                description="I require the ``Kick Members`` permisson to run this command - Missing Permission",
            )
            return await Context.send(embed=embed2)
        if member.id == Context.author.id:
            embed69 = nextcord.Embed(
                title="Kick Error",
                description="You sadly can not kick your self <a:sadboi:795385450978213938>",
            )
            return await Context.send(embed=embed69)
        elif Context.author.top_role.position < member.top_role.position:
            em3 = nextcord.Embed(
                title="Kick Error",
                description="Member **higher** than you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        elif Context.author.top_role.position == member.top_role.position:
            em3 = nextcord.Embed(
                title="Kick Error",
                description="Member has same role as you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        guild = Context.guild
        kickMsg = random.choice(kick_msg)
        kickEmbed = nextcord.Embed(
            title="Kick Success", description=f"{member.mention} {kickMsg}"
        )
        kickEmbed.add_field(name="Reason", value=reason)
        await Context.send(embed=kickEmbed)
        await member.send(f"You got kicked in **{guild}** | Reason: **{reason}**")
        await member.kick(reason=reason)

    @commands.command(name="tempmute", description="Mutes a member indefinitely.")
    @commands.has_permissions(manage_messages=True)
    async def tempmute(
        self, Context, member: nextcord.Member = None, time=None, *, reason=None
    ):
        guild = Context.guild
        if member == None:
            em1 = nextcord.Embed(
                title="Tempmute Error", description="Member to mute - Not Found"
            )
            return await Context.send(embed=em1)
        elif member.id == Context.author.id:
            em5 = nextcord.Embed(
                title="Tempmute Error", description="Don't bother, ive tried"
            )
            return await Context.send(embed=em5)
        if time == None:
            em2 = nextcord.Embed(
                title="Tempmute Error", description="Time to mute - Not Found"
            )
            return await Context.send(embed=em2)
        elif Context.author.top_role.position < member.top_role.position:
            em3 = nextcord.Embed(
                title="Tempmute Error",
                description="Member **higher** than you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        if not (Context.guild.me.guild_permissions.manage_roles):
            embed2 = nextcord.Embed(
                title="Tempmute Error",
                description="I require the ``Manage Roles`` permisson to run this command - Missing Permission",
            )
            return await Context.send(embed=embed2)
        elif Context.author.top_role.position == member.top_role.position:
            em4 = nextcord.Embed(
                title="Tempmute Error",
                description="Member has same role as you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em4)
        mutedRole = nextcord.utils.get(guild.roles, name="Muted")
        if Context.guild.me.top_role.position < mutedRole.position:
            em3 = nextcord.Embed(
                title="Tempmute Error",
                description="Muted role too high to give to a member",
            )
            return await Context.send(embed=em3)
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
            await Context.send("No mute role found. Creating mute role...")
            for channel in guild.channels:
                await channel.set_permissions(
                    mutedRole,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                )

        if not time == None:
            time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            tempmute = int(time[0]) * time_convert[time[-1]]
            embed = nextcord.Embed(
                title="Tempmute Success",
                description=f"{member.mention} was muted ",
                colour=nextcord.Colour.blue(),
            )
            embed.add_field(name="Reason:", value=reason, inline=False)
            embed.add_field(name="Duration", value=time)
            await Context.send(embed=embed)
            await member.add_roles(mutedRole, reason=reason)
            await member.send(
                f"You have been muted from: **{guild.name}** | Reason: **{reason}** | Time: **{time}**"
            )
            if not time == None:
                await asyncio.sleep(tempmute)
                await member.remove_roles(mutedRole)
                await member.send(f"You have been unmuted from **{guild}**")
            return

    @commands.command(
        name="mute", description="Mutes a member for a specific amount of time."
    )
    @commands.has_permissions(manage_messages=True)
    async def mute(self, Context, member: nextcord.Member = None, *, reason=None):
        guild = Context.guild
        if member == None:
            em1 = nextcord.Embed(
                title="Mute Error", description="Member to mute - Not Found"
            )
            return await Context.send(embed=em1)
        elif member.id == Context.author.id:
            em5 = nextcord.Embed(
                title="Mute Error", description="Don't bother, ive tried"
            )
            return await Context.send(embed=em5)
        elif Context.author.top_role.position < member.top_role.position:
            em3 = nextcord.Embed(
                title="Mute Error",
                description="Member **higher** than you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        elif Context.author.top_role.position == member.top_role.position:
            em4 = nextcord.Embed(
                title="Mute Error",
                description="Member has same role as you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em4)
        if not (Context.guild.me.guild_permissions.manage_roles):
            embed2 = nextcord.Embed(
                title="Mute Error",
                description="I require the ``Manage Roles`` permisson to run this command - Missing Permission",
            )
            return await Context.send(embed=embed2)
        mutedRole = nextcord.utils.get(guild.roles, name="Muted")
        if Context.guild.me.top_role.position < mutedRole.position:
            em3 = nextcord.Embed(
                title="Mute Error",
                description="Muted role too high to give to a member",
            )
            return await Context.send(embed=em3)
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
            await Context.send("No mute role found. Creating mute role...")
            for channel in guild.channels:
                await channel.set_permissions(
                    mutedRole,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                )

        embed = nextcord.Embed(
            title="Mute Success",
            description=f"{member.mention} was muted ",
            colour=nextcord.Colour.blue(),
        )
        embed.add_field(name="Reason:", value=reason, inline=False)
        await Context.send(embed=embed)
        await member.add_roles(mutedRole, reason=reason)
        await member.send(
            f"You have been muted from: **{guild.name}** | Reason: **{reason}**"
        )
        return

    @commands.command(name="unmute", description="Unmutes a muted member.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, Context, member: nextcord.Member = None, *, reason=None):
        guild = Context.guild
        if member == None:
            em1 = nextcord.Embed(
                title="Unmute Error", description="Member to unmute - Not Found"
            )
            return await Context.send(embed=em1)
        elif member.id == Context.author.id:
            em5 = nextcord.Embed(
                title="Unmute Error", description="wHat? <:WHA:815331017854025790>"
            )
            return await Context.send(embed=em5)
        elif Context.author.top_role.position < member.top_role.position:
            em3 = nextcord.Embed(
                title="Unmute Error",
                description="Member **higher** than you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em3)
        elif Context.author.top_role.position == member.top_role.position:
            em4 = nextcord.Embed(
                title="Unmute Error",
                description="Member has same role as you in the role heirarchy - Invalid Permission",
            )
            return await Context.send(embed=em4)
        if not (Context.guild.me.guild_permissions.manage_roles):
            embed2 = nextcord.Embed(
                title="Unmute Error",
                description="I require the ``Manage Roles`` permisson to run this command - Missing Permission",
            )
            return await Context.send(embed=embed2)
        mutedRole = nextcord.utils.get(guild.roles, name="Muted")
        if Context.guild.me.top_role.position < mutedRole.position:
            em3 = nextcord.Embed(
                title="Unmute Error",
                description="Muted role too high to remove from a member",
            )
            return await Context.send(embed=em3)
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
            await Context.send("No mute role found. Creating mute role...")
            for channel in guild.channels:
                await channel.set_permissions(
                    mutedRole,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                )

        embed = nextcord.Embed(
            title="Unmute Success",
            description=f"{member.mention} was unmuted ",
            colour=nextcord.Colour.blue(),
        )
        embed.add_field(name="Reason:", value=reason, inline=False)
        await Context.send(embed=embed)
        await member.remove_roles(mutedRole, reason=reason)
        await member.send(
            f"You have been unmuted from: **{guild.name}** | Reason: **{reason}**"
        )
        return

    @commands.command(description="Clears a bundle of messages.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, Context, amount=10):
        amount = amount + 1
        if amount > 101:
            em1 = nextcord.Embed(
                title="Clear Error",
                description="Purge limit exedeed - Greater than 100",
            )
            return await Context.send(embed=em1)
        else:
            await Context.channel.purge(limit=amount)
            msg = await Context.send("Cleared Messages")
            asyncio.sleep(10)
            await msg.delete()

    @commands.command(description="Change the channels slowmode.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, Context, time: int):
        try:
            if time == 0:
                em1 = nextcord.Embed(
                    title="Slowmode Success", description="Slowmode turned off"
                )
                await Context.send(embed=em1)
                await Context.channel.edit(slowmode_delay=0)
            elif time > 21600:
                em2 = nextcord.Embed(
                    title="Slowmode Error", description="Slowmode over 6 hours"
                )
                await Context.send(embed=em2)
            else:
                await Context.channel.edit(slowmode_delay=time)
                em3 = nextcord.Embed(
                    title="Slowmode Success",
                    description=f"Slowmode set to {time} seconds",
                )
                await Context.send(embed=em3)
        except Exception:
            await Context.send("Error has occoured, notifying dev team")
            print(Exception)

    @commands.command(
        aliases=["giverole", "addr"], description="Gives a member a certain role."
    )
    @commands.has_permissions(manage_roles=True)
    async def addrole(
        self, Context, member: nextcord.Member = None, *, role: nextcord.Role = None
    ):
        if member is None:
            embed = nextcord.Embed(
                title="Add Role Error",
                description="Please ping a user to give them a role!",
            )
            await Context.send(embed=embed)
            return
        if role is None:
            embed = nextcord.Embed(
                title="Add Role Error",
                description="Please ping a role to give {} that role!".format(
                    member.mention
                ),
            )
            await Context.send(embed=embed)
            return
        if Context.author.top_role.position < role.position:
            em = nextcord.Embed(
                title="Add Role Error",
                description="You do not have enough permissions to give this role",
            )
            return await Context.send(embed=em)
        if Context.guild.me.top_role.position < role.position:
            embed = nextcord.Embed(
                title="Add Role Error",
                description="That role is too high for me to perform this action",
            )
            return await Context.send(embed=embed)
        try:
            addRole = True
            for role_ in member.roles:
                if role_ == role:
                    addRole = False
                    break
            if not addRole:
                embed = nextcord.Embed(
                    title="Add Role Error",
                    description=f"{member.mention} already has the role you are trying to give",
                )
                await Context.send(embed=embed)
                return
            else:
                em = nextcord.Embed(
                    title="Add Role Success",
                    description=f"{role.mention} has been assigned to {member.mention}",
                )
                await Context.send(embed=em)
                await member.add_roles(role)
                return
        except Exception:
            print(Exception)

    @commands.command(
        aliases=["takerole", "remover"],
        description="Removes a certain role from a member.",
    )
    @commands.has_permissions(manage_roles=True)
    async def removerole(
        self,
        Context,
        member: nextcord.Member = None,
        role: nextcord.Role = None,
        *,
        reason=None,
    ):
        if member is None:
            embed = nextcord.Embed(
                title="Remove Role Error",
                description="Please ping a user to remove a role from them!",
            )
            await Context.send(embed=embed)
            return
        if role is None:
            embed = nextcord.Embed(
                title="Remove Role Error",
                description="Please ping a role to remove the role from {}!".format(
                    member.mention
                ),
            )
            await Context.send(embed=embed)
            return
        if Context.author.top_role.position < role.position:
            em = nextcord.Embed(
                title="Remove Role Error",
                description="You do not have enough permissions to remove this role",
            )
            return await Context.send(embed=em)
        if Context.guild.me.top_role.position < role.position:
            embed = nextcord.Embed(
                title="Remove Role Error",
                description="That role is too high for me to perform this action",
            )
            return await Context.send(embed=embed)
        try:
            roleRemoved = False
            for role_ in member.roles:
                if role_ == role:
                    await member.remove_roles(role)
                    roleRemoved = True
                    break
            if not roleRemoved:
                embed = nextcord.Embed(
                    title="Remove Role Error",
                    description=f"{member.mention} already has the role you are trying to give",
                )
                await Context.send(embed=embed)
                return
            else:
                em = nextcord.Embed(
                    title="Remove Role Success!",
                    description=f"{role.mention} has been removed from {member.mention}",
                )
                await Context.send(embed=em)
                return
        except Exception:
            print(Exception)

    @commands.command(description="Locks the channel.")
    @commands.has_permissions(kick_members=True)
    async def lock(self, Context, channel: nextcord.TextChannel = None, setting=None):
        if setting == "--server":
            view = LockConfirm()
            em = nextcord.Embed(
                title="Are you sure?",
                description="This is a very risky command only to be used in important situations such as, `Raid on the Server`. **If this command is used for the wrong purpose you may risk getting demoted if not banned from the staff team.**",
            )
            await Context.author.send(embed=em, view=view)
            await view.wait()
            if view.value is None:
                await Context.author.send(
                    "Command has been Timed Out, please try again."
                )
            elif view.value:
                for channel in Context.guild.channels:
                    await channel.set_permissions(
                        Context.guild.default_role,
                        reason=f"{Context.author.name} locked {channel.name} using --server override",
                        send_messages=False,
                    )
                embed = nextcord.Embed(
                    title="Lockdown Success",
                    description=f"Locked entire server <:saluteboi:897263732948885574>",
                )
                await Context.send(embed=embed)
            else:
                lockEmbed = nextcord.Embed(
                    title="Lock Cancelled",
                    description="Lets pretend like this never happened them :I",
                )
                await Context.author.send(embed=lockEmbed)
            return
        if channel is None:
            channel = Context.message.channel
        await channel.set_permissions(
            Context.guild.default_role,
            reason=f"{Context.author.name} locked {channel.name}",
            send_messages=False,  #
        )
        embed = nextcord.Embed(
            title="Lockdown Success",
            description=f"Locked {channel.mention} <:saluteboi:897263732948885574>",
        )
        await Context.send(embed=embed)

    @commands.command(description="Unlocks the channel.")
    @commands.has_permissions(kick_members=True)
    async def unlock(self, Context, channel: nextcord.TextChannel = None, setting=None):
        if setting == "--server":
            for channel in Context.guild.channels:
                await channel.set_permissions(
                    Context.guild.default_role,
                    reason=f"{Context.author.name} unlocked {channel.name} using --server override",
                    send_messages=None,
                )
            embed = nextcord.Embed(
                title="Unlock Success",
                description=f"Unlocked entire server (you might have to manualy relock servers that shouldnt have been unlocked)",
            )
            await Context.send(embed=embed)
            return
        if channel is None:
            channel = Context.channel
        await channel.set_permissions(
            Context.guild.default_role,
            reason=f"{Context.author.name} unlocked {channel.name}",
            send_messages=True,
        )
        embed = nextcord.Embed(
            title="Unlock Success",
            description=f"Unlocked {channel.mention} <:happyboi:804920510508433428>",
        )
        await Context.send(embed=embed)

    @commands.command(description="Modbans the member.")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def modban(self, Context, member, *, reason=None):
        if reason is None:
            reason = f"{Context.author.name} modbanned {member.name}"
        else:
            reason = f"{Context.author.name} modbanned {member.name} for the reason of {reason}"
        if member == None:
            embed1 = nextcord.Embed(
                title="Ban Error", description="Member to ban - Not Found"
            )
            return await Context.send(embed=embed1)
        if member.id == Context.author.id:
            embed69 = nextcord.Embed(
                title="Ban Error",
                description="Can not ban yourself, trust me I woulda ages ago <:hehe:796743161208504320>",
            )
            return await Context.send(embed=embed69)
        em = nextcord.Embed(
            title="Are you sure?",
            description="This is a very risky command only to be used in important situations such as, `NSFW or NSFLPosting` or `Raid on the Server`. Only use this command if no admin is online or responding. **If this command is used for the wrong purpose you may risk getting demoted if not banned from the staff team.**",
        )
        view = BanConfirm()
        await Context.author.send(embed=em, view=view)
        await view.wait()
        if view.value is None:
            await Context.author.send("Command has been Timed Out, please try again.")
        elif view.value:
            guild = Context.guild
            banMsg = random.choice(ban_msg)
            banEmbed = nextcord.Embed(
                title="Ban Success", description=f"{member.mention} {banMsg}"
            )
            banEmbed.add_field(name="Reason", value=reason)
            await Context.author.send(embed=banEmbed)
            await member.ban(reason=reason)
            await member.send(f"You got banned in **{guild}** | Reason: **{reason}**")
        else:
            banEmbed = nextcord.Embed(
                title="Ban Cancelled",
                description="Lets pretend like this never happened them :I",
            )
            await Context.author.send(embed=banEmbed)

    @commands.group(
        invoke_without_command=True, aliases=["sb", "starb"], description="A starboard"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def starboard(self, Context):
        try:
            guild_starboard_settings = read_database()[str(Context.guild.id)][
                "starboard"
            ]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            embed.set_footer(text="P.S. Use `>help starboard` for more info!")
            return await Context.send(embed=embed)
        embed = Embed(title=f"{Context.guild.name}'s Starboard Settings")
        embed.add_field(
            name="Status",
            value="Enabled"
            if guild_starboard_settings["on or off"] == True
            else "Disabled",
        )
        embed.add_field(
            name="Channel", value=f"<#{guild_starboard_settings['channel']}>"
        )
        embed.add_field(
            name="Number Of Stars Before Announcing",
            value=str(guild_starboard_settings["minimum stars"]),
        )
        embed.set_footer(text="P.S. Use `>help starboard` for more info!")
        await Context.send(embed=embed)

    @starboard.command(description="Set up the starboard!")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def setup(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings = read_database()[str(Context.guild.id)][
                "starboard"
            ]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            ...
        else:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"The starboard is already setup for this server!\nUse `{PREFIX}starboard` to view the settings!\nDo you want to wipe all the data and start again?",
            )
            view = View()
            view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.red,
                    label="Yes",
                    custom_id="True",
                    emoji="✔️",
                )
            )
            view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.green,
                    label="No",
                    custom_id="False",
                    emoji="✖️",
                )
            )
            await Context.send(embed=embed, view=view)

            def check(i):
                return i.user.id == Context.author.id

            r = True
            while r:
                try:
                    res = await self.Bot.wait_for(
                        "interaction", check=check, timeout=60.0
                    )
                    if res.data["component_type"] != 2:
                        ...
                    elif res.data["custom_id"] == "True":
                        embed = Embed(
                            title="Success!",
                            color=Color.green(),
                            description="Let's start the setup!",
                        )
                        await Context.send(embed=embed)
                        r = False
                        ...
                    elif res.data["custom_id"] == "False":
                        embed = Embed(
                            title="Cancelled!",
                            description="**Nothing Happened**",
                            color=Color.red(),
                        )
                        await Context.send(embed=embed)
                        r = False
                        return
                except asyncio.TimeoutError:
                    return
        embed = Embed(
            title="Let's start the Starboard setup!",
            description="Where should I post the starboard?",
        )
        embed.set_footer(text="Send `cancel` to cancel!")
        await Context.send(embed=embed)
        retry = True

        def check(m):
            return m.author.id == Context.author.id

        while retry:
            try:
                response = await self.Bot.wait_for("message", check=check, timeout=60.0)
                if response.content == "cancel":
                    retry = False
                    await Context.send(
                        embed=Embed(color=Color.red(), description="Cancelling...")
                    )
                else:
                    try:
                        channel_to_post_in = (
                            await commands.TextChannelConverter().convert(
                                Context, response.content
                            )
                        )
                        try:
                            database[str(Context.guild.id)]
                        except:
                            database[str(Context.guild.id)] = {}
                        database[str(Context.guild.id)]["starboard"] = {}
                        database[str(Context.guild.id)]["starboard"][
                            "channel"
                        ] = channel_to_post_in.id
                        database[str(Context.guild.id)]["starboard"]["on or off"] = True
                        embed = Embed(
                            title="Success!",
                            color=Color.green(),
                            description=f"The starboard will be sent to {channel_to_post_in.mention}",
                        )
                        await Context.send(embed=embed)
                        embed = Embed(
                            description="What should be the minimum star amount?"
                        )
                        await Context.send(embed=embed)
                        re = True
                        while re:
                            try:
                                response = await self.Bot.wait_for(
                                    "message", check=check, timeout=60.0
                                )
                                if response.content == "cancel":
                                    re = False
                                    await Context.send(
                                        embed=Embed(
                                            description="Cancelling....",
                                            color=Color.red(),
                                        )
                                    )
                                else:
                                    try:
                                        int(response.content)
                                        database[str(Context.guild.id)]["starboard"][
                                            "minimum stars"
                                        ] = response.content
                                        await Context.send(
                                            embed=Embed(
                                                title="Success!",
                                                color=Color.green(),
                                                description=f"Successfully set the minimum amount of stars to `{response.content}`",
                                            )
                                        )
                                        re = False
                                        view = nextcord.ui.View()
                                        view.add_item(
                                            nextcord.ui.Button(
                                                style=nextcord.ButtonStyle.green,
                                                label="Save",
                                                custom_id="True",
                                                emoji="✔️",
                                            )
                                        )
                                        view.add_item(
                                            nextcord.ui.Button(
                                                label="Cancel",
                                                style=nextcord.ButtonStyle.danger,
                                                emoji="✖️",
                                                custom_id="False",
                                            )
                                        )

                                        def check(i):
                                            return i.user.id == Context.author.id

                                        embed = Embed(
                                            title="Do you want to save the changes?"
                                        )
                                        await Context.send(embed=embed, view=view)
                                        r = True
                                        while r:
                                            try:
                                                res = await self.Bot.wait_for(
                                                    "interaction",
                                                    check=check,
                                                    timeout=60.0,
                                                )
                                                if res.data["component_type"] != 2:
                                                    ...
                                                elif res.data["custom_id"] == "True":
                                                    write_database(data=database)
                                                    embed = Embed(
                                                        title="Success!",
                                                        color=Color.green(),
                                                        description="The changes were successfully saved!",
                                                    )
                                                    await Context.send(embed=embed)
                                                    r = False
                                                elif res.data["custom_id"] == "False":
                                                    embed = Embed(
                                                        title="Cancelled!",
                                                        description="The changes were not saved!",
                                                        color=Color.red(),
                                                    )
                                                    await Context.send(embed=embed)
                                                    r = False
                                            except asyncio.TimeoutError:
                                                embed = Embed(
                                                    description="Let's pretend that never happened!"
                                                )
                                                return await Context.send(embed=embed)
                                    except commands.BadArgument:
                                        embed = Embed(
                                            title="Error!",
                                            description=f"Can't convert `{response.content}` to a number, try again.",
                                            color=Color.red(),
                                        )
                                        await Context.send(embed=embed)
                            except asyncio.TimeoutError:
                                embed = Embed(
                                    description="Let's pretend that never happened!"
                                )
                                return await Context.send(embed=embed)
                                re = False
                        retry = False
                    except commands.BadArgument:
                        embed = Embed(
                            title="Error!",
                            color=Color.red(),
                            description="I can't find that channel ;-;",
                        )
                        await Context.send(embed=embed)
            except asyncio.TimeoutError:
                embed = Embed(description="Let's pretend that never happened!")
                return await Context.send(embed=embed)
                retry = False

    @starboard.group(invoke_without_command=True, description="Toggle the starboard!")
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        embed = Embed(
            title=f"My Starboard Settings For {Context.guild.name}",
            color=Color.green()
            if guild_starboard_settings["on or off"]
            else Color.red(),
            description=f"The starboard is `{'Enabled' if guild_starboard_settings['on or off'] else 'Disabled'}` for this server.",
        )
        await Context.send(embed=embed)

    @toggle.command(
        aliases=["enable", "true", "enabled", "+"], description="Toggle the starboard!"
    )
    @commands.has_permissions(manage_guild=True)
    async def on(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        if guild_starboard_settings["on or off"]:
            return await Context.send(
                embed=Embed(
                    title="Error!",
                    description="The starboard for this server is already enabled!",
                    color=Color.red(),
                )
            )
        guild_starboard_settings["on or off"] = True
        write_database(data=database)
        await Context.send(
            embed=Embed(
                title="Success!",
                color=Color.green(),
                description="The starboard has been `enabled` for this server!",
            )
        )

    @toggle.command(
        aliases=["disable", "false", "disabled", "-"],
        description="Toggle the starboard!",
    )
    @commands.has_permissions(manage_guild=True)
    async def off(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        if not guild_starboard_settings["on or off"]:
            return await Context.send(
                embed=Embed(
                    title="Error!",
                    description="The starboard for this server is already disabled!",
                    color=Color.red(),
                )
            )
        guild_starboard_settings["on or off"] = False
        write_database(data=database)
        await Context.send(
            embed=Embed(
                title="Success!",
                color=Color.red(),
                description="The starboard has been `disabled` for this server!",
            )
        )

    @starboard.group(
        aliases=["ch"],
        invoke_without_command=True,
        description="Get the current starboard channel setting",
    )
    @commands.has_permissions(manage_guild=True)
    async def channel(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)

        await Context.send(
            embed=Embed(
                title=f"My Starboard Channel Settings For {Context.guild.name}",
                color=Color.green(),
                description=f"I post the starboard in <#{guild_starboard_settings['channel']}>",
            )
        )

    @channel.command(
        aliases=["set"], description="Change the current starboard channel setting"
    )
    @commands.has_permissions(manage_guild=True)
    async def change(Context, *, channel=None):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        try:
            channel_to_post_in = await commands.TextChannelConverter().convert(
                Context, channel
            )
            guild_starboard_settings["channel"] = channel_to_post_in.id
            write_database(data=database)
            await Context.send(
                embed=Embed(
                    title="Success!",
                    color=Color.green(),
                    description=f"Successfully set the starboard channel to {channel_to_post_in.mention}(#{channel_to_post_in.name})",
                )
            )
        except:
            await Context.send(
                embed=Embed(
                    title="Error!",
                    color=Color.red(),
                    description="I wasn't able to find that channel ;-;",
                )
            )

    @starboard.group(
        invoke_without_command=True,
        aliases=["minstars", "min-stars", "mins", "ms"],
        description="Get the current starboard minimum star setting",
    )
    async def minimum_stars(self, Context):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        await Context.send(
            embed=Embed(
                title=f"My Starboard Minimum Stars Settings For {Context.guild.name}",
                color=Color.green(),
            )
        )

    @minimum_stars.command(
        aliases=["set"], description="Change the current starboard minimum star setting"
    )
    @commands.has_permissions(manage_guild=True)
    async def change(Context, *, number):
        database = read_database()
        try:
            guild_starboard_settings = database[str(Context.guild.id)]["starboard"]
            guild_starboard_settings["on or off"]
            guild_starboard_settings["channel"]
            guild_starboard_settings["minimum stars"]
        except:
            embed = Embed(
                title="Starboard Error!",
                color=Color.red(),
                description=f"You don't have your starboard setup!, use `{PREFIX}starboard setup` to set it up!",
            )
            return await Context.send(embed=embed)
        try:
            number = int(number)
            guild_starboard_settings["minimum stars"] = number
            write_database(data=database)
            await Context.send(
                embed=Embed(
                    title="Success!",
                    color=Color.green(),
                    description=f"Successfully set the starboard minimum stars requirement to {number}",
                )
            )
        except:
            await Context.send(
                embed=Embed(
                    title="Error!",
                    color=Color.red(),
                    description="I wasn't able to convert the number to an integer ;-;",
                )
            )


def setup(Bot):
    Bot.add_cog(Moderation(Bot))
