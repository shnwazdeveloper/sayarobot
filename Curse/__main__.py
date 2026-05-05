from Curse.bot_class import app

try:
    import uvloop
except ImportError:
    uvloop = None

if __name__ == "__main__":
    if uvloop:
        uvloop.install()
    app().run()
