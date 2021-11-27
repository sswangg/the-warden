from discord.ext import commands
from discord.utils import get
import asyncio
import discord


def is_authority():
    """Checks that a member is a mod"""
    async def predicate(ctx):
        return "Authority Ping" in [r.name for r in ctx.author.roles]
    return commands.check(predicate)


def can_banish():
    """Checks that a member is a part of the shadowy organization that runs the world"""
    async def predicate(ctx):
        return ctx.author.id in [380550351423537153, 363690578950488074]
    return commands.check(predicate)


# Change this (maybe)
def jail_roles(member: discord.Member):
    """Returns all jail roles that a member has"""
    j_roles = [get(member.guild.roles, name="Horny inmate"), get(member.guild.roles, name="Horny Inmate 0001"),
               get(member.guild.roles, name="Horny Inmate 0002"),
               get(member.guild.roles, name="Horny Inmate 0003"),
               get(member.guild.roles, name="MAXIMUM SECURITY HORNY MF"),
               get(member.guild.roles, name="Banished")]
    member_roles = []
    for role in j_roles:
        if role in member.roles:
            member_roles.append(role)
    print(j_roles)
    print(member, member_roles)
    print(member.roles)
    return member_roles


class Moderation(commands.Cog):
    """BONK! These commands can be used by users with the role Authority Ping to jail and release other users."""
    def __init__(self, bot):
        self.bot = bot
        self.jailed = set()  # Keep track of who"s currently in jail for timer release purposes
        self.jail_dict = {"max": "MAXIMUM SECURITY HORNY MF",
                          "1": "Horny Inmate 0001",
                          "2": "Horny Inmate 0002",
                          "3": "Horny Inmate 0003"}
        self.timers = {}

    async def timer(self, ctx, duration, member):
        """Makes an auto-release timer"""
        await asyncio.sleep(duration)
        if member in self.jailed:
            member = await member.guild.fetch_member(member.id)
            await ctx.invoke(self.bot.get_command("release"), member=member)
            self.jailed.discard(member)

    @commands.command(
        brief="Sends a member to horny jail",
        usage="owo bonk <user> [cell] [time]",
        help="This command can only be used by people with the role Authority Ping. "
             "It gives a member the Horny inmate role, along with a role for the cell that they're assigned to, "
             "defaulting to sending users to cell 1 for 30 minutes. Specify cell using '1', '2', '3', or 'max', "
             "and time using a number in minutes.\n"
             "\n"
             "[Examples]\n"
             "[1] owo bonk floop#6996 max 10\n"
             "[2] owo bonk Weebaoo 2\n"
             "[3] owo bonk 409822116955947018")
    @is_authority()
    async def bonk(self, ctx, member: discord.Member, cell="1", sentence_time: int = 30):
        if get(member.guild.roles, name="Server Booster") in member.roles or \
                get(member.guild.roles, name="Authority Ping") in member.roles:
            await ctx.channel.send("This member cannot be bonked")
            return
        if sentence_time <= 0:
            await ctx.channel.send("?????????????\nPlease jail people for 1 or more minutes")
            return
        # Remove all previous jail roles
        if j_roles := jail_roles(member):
            await member.remove_roles(*j_roles)
            await ctx.channel.send("Freed prisoner... ready for transport")
        # Gets jail roles
        horny_role = get(member.guild.roles, name="Horny inmate")
        cell_role = get(member.guild.roles, name=self.jail_dict[cell.lower()])
        if cell.lower() == "max":
            cell = "maximum security"
            sentence_time = 60
        else:
            cell = "cell " + cell
            if cell_role is None:
                await ctx.channel.send("That is not a valid cell")
                return
        await ctx.channel.send(f"Sent {member} to {cell} in horny jail for {sentence_time} minutes")
        await member.add_roles(horny_role, cell_role)  # Bonk
        self.jailed.add(member)
        self.timers[member] = asyncio.create_task(self.timer(ctx, sentence_time * 60, member))

    @commands.command(
        brief="Banishes a member to THE SHADOW REALM™️",
        usage="owo banish <user>",
        help="This mysterious command can only be used by Alain.\n"
             "Basically soft-bans people\n")
    @can_banish()
    async def banish(self, ctx, member: discord.Member):
        role = get(member.guild.roles, name="Banished")
        if role in member.roles:
            await ctx.channel.send(f"{member} is already in THE SHADOW REALM™️")
            return
        if j_roles := jail_roles(member):
            await member.remove_roles(*j_roles)
            await ctx.channel.send(f"Freed prisoner... ready for transport")
        await member.add_roles(role)
        self.jailed.add(member)
        await ctx.channel.send(f"Banished {member} to THE SHADOW REALM™️")

    @commands.command(
        brief="Releases someone from the depths",
        usage="owo release <user>",
        help="This command can only be used by people with the role Authority Ping.\n"
             "It removes all horny jail roles from a member, and also removes the banished role if the person using the"
             " command is Alain.")
    @is_authority()
    async def release(self, ctx, member: discord.Member):
        banish_role = get(member.guild.roles, name="Banished")  # Shadow realm role
        if jail_roles(member):  # Only run if the member is in jail
            if banish_role in member.roles:  # Unbanish if applicable
                if can_banish():
                    await member.remove_roles(banish_role)
                    await ctx.channel.send(f"Released {member} from THE SHADOW REALM™️")
                    self.jailed.discard(member)
                else:
                    await ctx.channel.send("You don't have permission to release from THE SHADOW REALM™️")
            if j_roles := jail_roles(member):  # Unbonk
                await ctx.channel.send(f"Released {member} from horny jail")
                await member.remove_roles(*j_roles)
                try:
                    self.timers[member].cancel()
                except KeyError:
                    pass
                self.jailed.discard(member)
        else:
            await ctx.channel.send(f"There is nothing to release {member} from!")
            return


def setup(bot):
    bot.add_cog(Moderation(bot))
