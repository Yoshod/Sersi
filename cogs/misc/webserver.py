import nextcord
from aiohttp import web
from nextcord.ext import commands

from utils.config import Configuration

app = web.Application()
routes = web.RouteTableDef()

# http://77.68.125.175:8113


class WebServer(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

        @routes.get("/")
        def uptimerobot(request: web.Request):
            return web.Response(text="Pong!", status=200)

        app.add_routes(routes)

    @commands.Cog.listener()
    async def on_ready(self):
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, port=self.config.bot.port)
        await site.start()
        print(f"Started web server at {site.name}.")


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(WebServer(bot, kwargs["config"]))
