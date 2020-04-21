# Interact with Discord
import discord

# Get URLs to derpibooru images
import derpibooru

# Download the images from those URLs
import requests

# For converting image data to something discord.py will be happy to upload
from io import BytesIO

# Global configuration variables
search_command = "!derpi"
number_of_images_to_post = 3

client = discord.Client()
derpi_search_client = derpibooru.Search(limit=number_of_images_to_post)


@client.event
async def on_ready():
    print("I'm logged in")


@client.event
async def on_message(message):
    # Only process messages that start with our search command
    if not message.content.startswith(search_command):
        # Exit the function
        return

    # We want to transform the message content:
    # "!derpi twilight sparkle, pancake
    # into just the tags to search with:
    # "twilight sparkle, pancake"
    # So just cut off the first 7 characters of the message
    tags = message.content[7:]

    # Now we want to transform the tags:
    # "twilight sparkle, pancake"
    # Into a list that we can hand to the derpybooru library:
    # ["twilight sparkle", "pancake"]
    # The str (string) object's split() function can help us here
    tags = tags.split(",")

    # Now we can do a search!

    # for loops are things that let you run the same code over and over
    # but with a different variable value each time
    # Here, we run the indented code over and over, but on each iteration
    # set the value of the `image` variable to a different image returned
    # by the derpibooru.Search().query() method
    # Basically we're going through each image we find on derpibooru
    #
    # The * next to tags is interesting. You know how you can run a function
    # with multiple arguments? (Ex. kick_user_from_voice(voice_channel, user))
    # The * takes a list and turns each item into a separate argument to the function
    # So with a list: ["twilight", "applejack", "rarity"]
    # Whereas you could give the list to the function as one argument:
    # some_function(["twilight", "applejack", "rarity"])
    # You can instead make each item a separate argument for a total of 3
    # some_function("twilight", "applejack", "rarity")
    for image in derpi_search_client.query(*tags):
        # The image url is stored in a mapping from various
        # image size names to their download url.
        # We use "large" here, which is big but not the full size
        # The list of sizes is at https://derpibooru.org/pages/api#image-response
        # under "representations"
        #
        # Once we have the URL, we can use requests.get() to download the
        # image itself. We don't save this image to disk. Instead, we store
        # it in a variable, and then send the contents of that variable to
        # discord. We avoid the disk as it's relatively slow
        response = requests.get(image.representations["large"])
        image_data = response.content

        # Now we just need to create an instance of our old friend, discord.File,
        # but also explicitly set the filename, as we don't have one implicitly
        # since we're not uploading a file from the disk this time.
        #
        # Also, discord will only preview the image if the filename ends in
        # .png, .jpg, etc..
        #
        # Since images uploaded to derpibooru don't always have a filename
        # ending in one of these, we use some variables from the image object
        # to create a filename instead.
        #
        # str() converts an int/number (and a lot of other things) into a
        # str (string). We need to do this as you can't combine an int and a str,
        # you can only do so with a str and a str. So convert the int to a str!
        filename = str(image.id) + "." + image.format

        # Oh, and we need to wrap our image data in a BytesIO object, which is
        # basically just an object that you can easily get parts of a file from.
        # discord.py wants it for whatever reason
        file = BytesIO(image_data)

        # Ok, let's create our discord.File object!
        file = discord.File(file, filename=filename)

        # And upload that file to the channel where the message was sent
        await message.channel.send(file=file)


client.run('YOUR_BOT_TOKEN_HERE')
