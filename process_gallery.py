import os
from pathlib import Path
from PIL import Image

# --- Configuration ---
BASE_DIR = Path(__file__).parent
UNPROCESSED_DIR = BASE_DIR / 'assets' / 'images' / 'unprocessed'
OUTPUT_DIR = BASE_DIR / 'assets' / 'images' / 'photography'
HTML_FILE = BASE_DIR / 'photography' / 'index.html'

def get_aspect_ratio_class(width, height):
    """Determine Tailwind aspect ratio class based on dimensions."""
    ratio = width / height
    # Tolerance for square
    if 0.9 <= ratio <= 1.1:
        return "aspect-square"
    elif ratio > 1.1:
        return "aspect-video" # Landscape
    else:
        return "aspect-[4/5]" # Portrait

def process_images():
    # Supported input formats
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    
    # Read existing HTML to avoid duplicates
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {HTML_FILE}")
        return

    new_articles = []
    
    print(f"Scanning {UNPROCESSED_DIR}...")

    # Ensure output directory exists
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in UNPROCESSED_DIR.iterdir():
        if file_path.suffix.lower() not in valid_extensions:
            continue

        try:
            with Image.open(file_path) as img:
                # 1. Convert to WebP
                output_filename = f"{file_path.stem}.webp"
                output_path = OUTPUT_DIR / output_filename
                
                # Convert and save
                img.save(output_path, 'WEBP', quality=85)
                print(f"Converted: {file_path.name} -> {output_filename}")

                # 2. Prepare HTML (only if not already present)
                # We check for the filename in the HTML content to prevent duplicates
                if output_filename in html_content:
                    print(f"Skipping HTML entry: {output_filename} already exists in index.html")
                    continue

                # Determine aspect ratio for the class
                w, h = img.size
                aspect_class = get_aspect_ratio_class(w, h)
                
                # Format display name (e.g., "my-photo" -> "My Photo")
                display_name = file_path.stem.replace('-', ' ').replace('_', ' ').title()

                # Default category for the visual tag
                category = "urban"

                # Create HTML Snippet
                article_html = f"""
            <!-- {display_name} -->
            <article class="gallery-item group relative overflow-hidden bg-gray-200 dark:bg-gray-800 {aspect_class} rounded-sm cursor-zoom-in lightbox-trigger" data-category="{category}" data-full="../assets/images/photography/{output_filename}">
                <img src="../assets/images/photography/{output_filename}" alt="{display_name}" loading="lazy" onload="this.classList.add('loaded')" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105">
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end items-start p-4">
                    <span class="text-[9px] font-medium text-black bg-white/90 backdrop-blur-sm px-2 py-0.5 rounded-sm w-fit mb-2 uppercase tracking-widest">{category}</span>
                    <p class="text-white text-[10px] md:text-xs uppercase tracking-widest">
                        {display_name}
                    </p>
                </div>
            </article>"""
                
                new_articles.append(article_html)

        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")

    # 3. Inject into HTML
    if new_articles:
        # Find the gallery section by ID
        gallery_start_pos = html_content.find('id="gallery"')
        
        if gallery_start_pos != -1:
            # Find the closing tag for the section (assuming the next </section> closes the gallery)
            insert_pos = html_content.find('</section>', gallery_start_pos)
            
            if insert_pos != -1:
                updated_html = html_content[:insert_pos] + "\n".join(new_articles) + "\n        " + html_content[insert_pos:]
                
                with open(HTML_FILE, 'w', encoding='utf-8') as f:
                    f.write(updated_html)
                print(f"Successfully added {len(new_articles)} new items to index.html")
            else:
                print("Error: Could not find closing </section> tag for gallery.")
        else:
            print("Error: Could not find element with id='gallery'.")
    else:
        print("No new images to add to HTML.")

if __name__ == "__main__":
    process_images()