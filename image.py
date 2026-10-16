from PIL import Image

def create_wraparound_cover(front_cover_path, output_pdf_path, back_color="#1a0b2e"):
    # KDP Wraparound Dimensions at 300 DPI
    # 17.368 inches wide x 11.250 inches high
    target_width = int(17.368 * 300)  # 5210 pixels
    target_height = int(11.250 * 300) # 3375 pixels

    # Create the full canvas with the solid background color (back cover + spine)
    wraparound = Image.new('RGB', (target_width, target_height), back_color)

    try:
        # Load the front cover
        front_cover = Image.open(front_cover_path).convert('RGB')
        
        # The front cover occupies the right side of the wraparound.
        # Standard front cover with bleed is 8.625" x 11.25" (2588 x 3375 pixels).
        front_width = int(8.625 * 300)
        
        # Resize front cover to fit KDP's exact right-side dimensions
        front_cover = front_cover.resize((front_width, target_height), Image.Resampling.LANCZOS)
        
        # Calculate the X coordinate to paste the front cover (flush right)
        paste_x = target_width - front_width
        
        # Paste the front cover onto the right side of the canvas
        wraparound.paste(front_cover, (paste_x, 0))
        
        # Save the final file as a print-ready PDF
        wraparound.save(output_pdf_path, "PDF", resolution=300.0)
        print(f"Success! Wraparound cover saved to {output_pdf_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find the front cover image at '{front_cover_path}'")

# Run the pipeline
# Replace 'front_cover.jpg' with your actual filename
create_wraparound_cover('front_cover.jpg', 'kdp_wraparound_cover.pdf', back_color='#1a0b2e')
