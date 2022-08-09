from aiohttp import web
from nextcord.ext import commands, tasks


app    = web.Application()
routes = web.RouteTableDef()


class WebServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.web_server.start()

        @routes.get('/')
        def home(request):
            return web.Response(text="Hewwo UwutimeWowobowot!!!")

        app.add_routes(routes)


    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host="0.0.0.0", port=8113) # 8074 for live, 8113 for testing
        await site.start()


    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(WebServer(bot))
