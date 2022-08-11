import asyncio
import nextcord
import xmltodict

from aiohttp import web
from aiohttp.web import Request
from nextcord.ext import commands
from typing import Any

from configuration.configuration import Configuration
from sersi import Sersi


app    = web.Application()
routes = web.RouteTableDef()


class WebServer(commands.Cog, name="Web server", description="HTTP serving and management."):
    def __init__(self, bot: Sersi, config: Configuration):
        self.bot    = bot
        self.config = config

        @routes.get("/")
        def uptimerobot(request):
            return web.Response(text="Hewwo UwuptimeWowobowot!!!", status=200)

        @routes.get("/youtube")
        async def youtube_verification(request: Request):
            if request.query is None or {"hub.challenge", "hub.mode", "hub.topic"} <= request.query.keys():
                return web.Response(text="Invalid PuSH query", status=400)

            if not request.query["hub.topic"].startswith("https://www.youtube.com/xml/feeds/videos.xml?channel_id="):
                return web.Response(text="Invalid topic", status=400)

            match request.query["hub.mode"]:
                case "subscribe":
                    print(f"[web_server] subscribed to {request.query['hub.topic']}")

                case "unsubscribe":
                    print(f"[web_server] unsubscribed from {request.query['hub.topic']}")

                case _:
                    return web.Response(text="Invalid mode", status=400)

            return web.Response(body=request.query["hub.challenge"].encode("utf8"), status=201)

        @routes.post("/youtube")
        async def youtube_notification(request: Request):
            if not request.has_body:
                return web.Response(text="No body given", status=400)

            data = xmltodict.parse(await request.read())

            origins = data["feed"]["link"]
            for origin in origins:
                if not origin["@rel"] == "self":
                    continue

                if origin["@href"].startswith("https://www.youtube.com/xml/feeds/videos.xml?channel_id="):
                    channel: nextcord.TextChannel = self.bot.get_channel(self.config.channels.youtube)
                    await channel.send(f"New video from {data['feed']['entry']['author']['name']}: **{data['feed']['entry']['title']}**\nWatch it here: **{data['feed']['entry']['link']['@href']}**")
                    return web.Response(status=201)
                else:
                    return web.Response(text="Topic ignored", status=204)

            return web.Response(text="Topic not found ", status=400)

        app.add_routes(routes)

    def cog_unload(self):
        asyncio.run_coroutine_threadsafe(app.shutdown(), asyncio.get_running_loop())
        super().cog_unload()

    @commands.Cog.listener()
    async def on_ready(self):
        runner = web.AppRunner(app)
        await runner.setup()

        if len(runner.sites) > 0:
            return

        site = web.TCPSite(runner, port=self.config.port)
        await site.start()


def setup(bot: Sersi, **kwargs: dict[str, Any]):
    bot.add_cog(WebServer(bot, kwargs["config"]))
