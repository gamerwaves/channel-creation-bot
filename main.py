import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import category_manager
import storage

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# TARGET_CATEGORY_ID is now managed by category_manager but we might still read it for initial setup if needed, 
# or we rely solely on the store. The plan implies the admin sets it. 
# However, to keep backward compatibility or easy setup, we can check env if store is empty.
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')

# Bot setup
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
<<<<<<< HEAD
        # Initialize category store from env if empty
        target_cat_env = os.getenv('TARGET_CATEGORY_ID')
        if target_cat_env and not category_manager.get_base_category_id():
            category_manager.set_base_category(target_cat_env)
            print(f"Initialized base category from .env: {target_cat_env}")
            
=======
>>>>>>> 0196648 (added delete functionality im too lazy to map ppl so yea...)
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command(name="set-category", description="Admin only: Set the base category for new channels")
@app_commands.describe(category_id="The ID of the base category")
async def set_category(interaction: discord.Interaction, category_id: str):
    if str(interaction.user.id) != ADMIN_USER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    try:
        # Verify it exists
        category = interaction.guild.get_channel(int(category_id))
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(f"Invalid category ID. Please provide a valid Category ID.", ephemeral=True)
            return
        
        category_manager.set_base_category(category_id)
        await interaction.response.send_message(f"Base category set to **{category.name}** (ID: {category_id}).", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid ID format.", ephemeral=True)

@client.tree.command(name="delete-channel", description="Admin only: Delete a channel")
@app_commands.describe(channel="The channel to delete")
async def delete_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if str(interaction.user.id) != ADMIN_USER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    try:
        await channel.delete()
        await interaction.response.send_message(f"Channel **{channel.name}** has been deleted.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to delete that channel.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"Failed to delete channel: {e}", ephemeral=True)


@client.tree.command(name="create-channel", description="Creates a new text channel")
@app_commands.describe(channel_name="The name of the channel to create")
async def create_channel(interaction: discord.Interaction, channel_name: str):
    # Check if user has reached the limit
    user_id = interaction.user.id
    current_count = storage.get_user_channel_count(user_id)
    
    if current_count >= 2:
        await interaction.response.send_message("You have reached the limit of 2 created channels.", ephemeral=True)
        return

    # Get the category via manager
    category = await category_manager.get_target_category(interaction.guild)
    
    if not category:
        await interaction.response.send_message("Configuration error: No valid category found or created. Please contact an admin.", ephemeral=True)
        return

    # Create the channel
    try:
        # Defer response since channel creation might take a moment
        await interaction.response.defer(ephemeral=True)
        
        new_channel = await interaction.guild.create_text_channel(name=channel_name, category=category)
        
        # Ping the user in the new channel
        await new_channel.send(f"Channel created {interaction.user.mention}!")

        # Save channel info
        storage.add_user_channel(user_id, new_channel.id, channel_name)
        
        await interaction.followup.send(f"Channel {new_channel.mention} created successfully in {category.name}!")
        
    except discord.Forbidden:
        await interaction.followup.send("I do not have permission to create channels in that category.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Failed to create channel: {e}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)

@client.tree.command(name="delete-channel", description="Deletes a channel you created")
@app_commands.describe(channel="The channel to delete")
async def delete_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    user_id = interaction.user.id
    user_channels = storage.get_user_channels(user_id)
    
    # Check if user created this channel
    channel_ids = [ch['id'] for ch in user_channels]
    if channel.id not in channel_ids:
        await interaction.response.send_message("You can only delete channels you created.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Delete the channel
        await channel.delete()
        
        # Remove from storage
        storage.remove_user_channel(user_id, channel.id)
        
        await interaction.followup.send(f"Channel '{channel.name}' deleted successfully!")
        
    except discord.Forbidden:
        await interaction.followup.send("I do not have permission to delete that channel.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Failed to delete channel: {e}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)

@client.tree.command(name="my-channels", description="Lists channels you have created")
async def my_channels(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_channels = storage.get_user_channels(user_id)
    
    if not user_channels:
        await interaction.response.send_message("You haven't created any channels yet.", ephemeral=True)
        return
    
    channel_list = "\n".join([f"• <#{ch['id']}> ({ch['name']})" for ch in user_channels])
    await interaction.response.send_message(
        f"**Your created channels ({len(user_channels)}/2):**\n{channel_list}",
        ephemeral=True
    )

if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env")
    else:
        client.run(TOKEN)
