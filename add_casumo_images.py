#!/usr/bin/env python3
"""
Add Casumo images to images.json
"""
import json

# Load existing images
with open('images.json', 'r') as f:
    data = json.load(f)

# Get the highest ID to generate new IDs
highest_id = max([img['id'] for img in data['attachments']])

# Define new Casumo images
new_images = [
    {
        "filename": "casumo-casino-popular-slot-games-lobby.webp",
        "title": "Casumo casino popular slot games lobby",
        "alt": "Casumo casino games lobby displaying popular slots like Gold Blitz Extreme and Rise of Olympus",
        "caption": "Casumo's top slots and featured games"
    },
    {
        "filename": "casumo-casino-welcome-bonus-popup.webp",
        "title": "Casumo casino welcome bonus popup",
        "alt": "Casumo casino pop-up showing 100% up to £100 and 50 bonus spins welcome offer",
        "caption": "Casumo Casino — welcome bonus with deposit match and spins"
    },
    {
        "filename": "casumo-sports-free-bet-uk-offer.webp",
        "title": "Casumo Sports free bet UK offer",
        "alt": "Casumo Sports homepage promoting 100% Free Bet up to £30 for new UK players",
        "caption": "Casumo Sports — 100% Free Bet welcome offer"
    },
    {
        "filename": "casumo-uk-deposit-bonus-promo.webp",
        "title": "Casumo UK deposit bonus promo",
        "alt": "Casumo casino banner advertising 100% deposit match up to £100 and 50 bonus spins",
        "caption": "Casumo deposit match bonus for new UK players"
    }
]

# Add new images to attachments
current_id = highest_id + 1

for img in new_images:
    attachment = {
        "id": current_id,
        "title": img["title"],
        "url": f"https://b3i.tech/wp-content/uploads/2025/11/{img['filename']}",
        "link": f"https://b3i.tech/{img['filename'].replace('.webp', '').replace('.png', '')}/",
        "status": "inherit",
        "pub_date": "Wed, 19 Nov 2025 12:00:00 +0000",
        "parent_id": 0,
        "metadata": {
            "_wp_attached_file": f"2025/11/{img['filename']}",
            "_wp_attachment_image_alt": img["alt"],
            "caption": img["caption"]
        }
    }
    data['attachments'].append(attachment)
    current_id += 1
    print(f"Added: {img['filename']} (ID: {attachment['id']})")

# Save updated JSON
with open('images.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nSuccessfully added {len(new_images)} Casumo images to images.json")
print(f"Total attachments: {len(data['attachments'])}")
