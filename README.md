🔮 Normal Map Generator Bot

A professional Telegram bot built with aiogram 3.x designed for game developers and 3D artists. This bot converts standard 2D textures into Normal Maps and offers additional tools like pixelation for retro-style assets.
✨ Features

    Normal Map Generation: Automatically creates a surface relief map (Normal Map) from any image.

    Adjustable Strength: Fine-tune the "depth" of the relief using an interactive menu.

    Pixelation Tool: Built-in downscaling/upscaling logic to create pixel-art style textures.

    Interactive UI: Fully managed via Inline Keyboards—no complicated commands needed.

    High Quality: Delivers results as uncompressed documents (PNG) to preserve pixel data for Unity, Unreal Engine, or Blender.

🛠 Tech Stack

    Language: Python 3.10+

    Bot Framework: aiogram 3.x (Asynchronous)

    Image Processing:

        Pillow (PIL) for image manipulation and resizing.

        NumPy for high-performance gradient calculations and vector normalization.

    Storage: MemoryStorage (FSM) for handling temporary user data and settings.

🚀 Installation & Setup
1. Clone the repository
code Bash

git clone https://github.com/your-username/normal-map-gen-bot.git
cd normal-map-gen-bot

2. Install dependencies
code Bash

pip install -r requirements.txt

3. Environment Variables

Create a .env file in the root directory:
code Env

BOT_TOKEN=your_telegram_bot_token_here

4. Run the bot
code Bash

python main.py

📂 Project Structure

    main.py — Entry point. Initializes the bot and registers routers.

    handlers/ — Logic for handling commands (common.py) and image uploads (images.py).

    services/processing.py — The core logic: NumPy-based Normal Map algorithm and pixelation filters.

    utils/ — Message templates (texts.py) and FSM state definitions (states.py).

    keyboards/builders.py — Dynamic inline keyboard generation for settings.

📝 How it Works

    Input: User sends a photo or an image file to the bot.

    Settings: The bot opens an interactive menu where you can:

        Increase/Decrease Pixelation (useful for pixel-art textures).

        Adjust Normal Strength (how "bumpy" the surface looks).

    Processing:

        The image is converted to grayscale (Height Map).

        Sobel-like filters (via NumPy gradients) calculate the surface normals.

        Data is normalized and mapped to the RGB space (0.5, 0.5, 1.0 being the neutral flat blue).

    Output: The bot sends back the processed Texture (Albedo) and the generated Normal Map as files.

⚙️ Example Parameters

    Pixelation: 1 (Off) to 20+ (Heavy pixel art).

    Strength: Default is 5.0. Higher values create more dramatic shadows and highlights in 3D engines.

⚠️ Requirements

See requirements.txt:

    aiogram

    python-dotenv

    Pillow

    numpy
