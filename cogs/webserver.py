import asyncio
import nextcord
import xmltodict

from aiohttp import web
from aiohttp.web import Request
from nextcord.ext import commands, tasks

from configuration.configuration import Configuration


app    = web.Application()
routes = web.RouteTableDef()


class WebServer(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot    = bot
        self.config = config

        self.web_server.start()

        @routes.get("/")
        def uptimerobot(request):
            return web.Response(text="Empty Request")

        @routes.get("/youtube")
        @routes.post("/youtube")
        async def youtube_update(request: Request):
            if request.query is not None and "hub.challenge" in request.query:
                print(f"[web_server] {request.query['hub.mode']} for {request.query['hub.topic']}")
                return web.Response(body=request.query["hub.challenge"].encode("utf8"), status=201)

            if not request.has_body:
                return web.Response(text="No body given", status=400)

            data = xmltodict.parse(await request.read())

            channel: nextcord.TextChannel = self.bot.get_channel(self.config.channels.youtube)
            if channel is None:
                raise Exception("YouTube text channel is none")

            channel_name = data['feed']['entry']['author']['name']
            video_title  = data['feed']['entry']['title']
            video_url    = data['feed']['entry']['link']['@href']

            await channel.send(f"New video from {channel_name}: **{video_title}**\nWatch it here: **{video_url}**")
            return web.Response(status=204)

        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, port=self.config.bot.port)

        try:
            await site.start()
        except OSError:  # TODO: tends to be port in use, check whether this is the cas
            await asyncio.sleep(5)
            return

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot, **kwargs):
    bot.add_cog(WebServer(bot, kwargs["config"]))
