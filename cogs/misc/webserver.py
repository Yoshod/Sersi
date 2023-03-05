import nextcord
import xmltodict
from aiohttp import web
from nextcord.ext import commands

from configutils import Configuration

app = web.Application()
routes = web.RouteTableDef()

# http://77.68.125.175:8113
# https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCE9-NjoFfHqekXmJLt5WMLg


class WebServer(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

        @routes.get("/")
        def uptimerobot(request: web.Request):
            return web.Response(text="Pong!", status=200)

        @routes.get("/youtube")
        async def youtube_verification(request: web.Request):

            if "hub.challenge" not in request.query:
                return web.Response(
                    text="403 You are not meant to be here.", status=403
                )

            match request.query["hub.mode"]:
                case "subscribe":
                    print(f"[web_server] subscribed to {request.query['hub.topic']}")

                case "unsubscribe":
                    print(
                        f"[web_server] unsubscribed from {request.query['hub.topic']}"
                    )

                case _:
                    return web.Response(text="Invalid mode", status=400)

            return web.Response(
                body=request.query["hub.challenge"].encode("utf8"), status=200
            )

        @routes.post("/youtube")
        async def youtube_update(request: web.Request):

            if not request.can_read_body:
                return web.Response(text="No body given", status=400)

            data = xmltodict.parse(await request.read())

            prev_vids = []
            try:
                with open(self.config.datafiles.video_history, "r") as file:
                    for line in file:
                        line = line.replace("\n", "")
                        prev_vids.append(line)

            except FileNotFoundError:
                with open(self.config.datafiles.video_history, "x"):
                    pass
                pass

            channel_name = data["feed"]["entry"]["author"]["name"]
            video_title = data["feed"]["entry"]["title"]
            video_url = data["feed"]["entry"]["link"]["@href"]
            video_id = data["feed"]["entry"]["yt:videoId"]

            if video_id in prev_vids:
                print(f"Recieved Update for Video {video_id}, nothing to be done.")
                return web.Response(status=204)

            print(f"Recieved Update for Video {video_id}, now processing.")
            with open(self.config.datafiles.video_history, "a") as file:
                file.write(f"{video_id}\n")

            # create announcement
            channel = self.bot.get_channel(self.config.channels.youtube)
            await channel.send(
                f"__**New {channel_name} Video**__\n{channel_name} has uploaded a video: {video_title} {video_url}\n@everyone"
            )

            # create forum post
            forum = self.bot.get_channel(self.config.channels.video_discussion)
            messagestr = f"New video by {channel_name}: {video_url}"
            await forum.create_thread(
                name=video_title, content=messagestr, reason="Creating Video Thread"
            )  # for some reason they call forum posts threads (they behave very similar)

            return web.Response(status=204)

        app.add_routes(routes)

    @commands.Cog.listener()
    async def on_ready(self):
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, port=self.config.bot.port)
        await site.start()
        print(f"Started web server at {site.name}.")


def setup(bot, **kwargs):
    bot.add_cog(WebServer(bot, kwargs["config"]))
