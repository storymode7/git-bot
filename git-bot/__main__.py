import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()

@router.register("pull_request", action="opened")
async def pull_request_event(event, gh, *args, **kwargs):
    """ label the pull request when it's opened """
    url = event.data["pull_request"]["issue_url"]
    await gh.patch(url, data={"labels":"Needs Review"})

async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # add authentication token and webhook secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of github webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # pay attention to the username used 
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "storymode7", oauth_token=oauth_token)

        # call appropriate callback for the event
        await router.dispatch(event, gh)

    # return "Success" response
    return web.Response(status=200)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)


