from PIL import Image
from pdf2image import convert_from_path

def create_wraparound_cover(front_cover_path, output_pdf_path, back_color="#1a0b2e"):
    # KDP Wraparound Dimensions at 300 DPI
    # 17.368 inches wide x 11.250 inches high
    target_width = int(17.368 * 300)  # 5210 pixels
    target_height = int(11.250 * 300) # 3375 pixels

    # Create the full canvas with the solid background color (back cover + spine)
    # Acting as a seamless background bleed so safety borders don't render as white
    wraparound = Image.new('RGB', (target_width, target_height), back_color)

    try:
        # Load the front cover
        front_cover = Image.open(front_cover_path).convert('RGB')
        
        # Original width with bleed is 8.625" x 11.25"
        front_width_original = int(8.625 * 300) # 2588 pixels
        
        # RED ZONE FIX: Downscale the front cover slightly (e.g. 92%)
        # and wrap it inside the dark theme. This keeps text and characters
        # well clear of KDP’s red dotted cutoff margins.
        safe_scale_factor = 0.92
        scaled_width = int(front_width_original * safe_scale_factor)
        scaled_height = int(target_height * safe_scale_factor)
        
        # Resize to safe, shrunken dimensions
        front_cover_safe = front_cover.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # Set alignment padding inside the wraparound.
        # Shift slightly left from the absolute edge (x-pad) and center vertically (y-pad).
        padding_right = 110 # Pulls the artwork inward from the outer right trim
        padding_top = (target_height - scaled_height) // 2 # Centers top-to-bottom
        
        # paste_x anchors the front cover's left edge on the canvas
        paste_x = target_width - scaled_width - padding_right
        paste_y = padding_top
        
        # Paste the safely sized front cover on the right side of the canvas
        wraparound.paste(front_cover_safe, (paste_x, paste_y))
        
        # Save the final file as a print-ready PDF
        wraparound.save(output_pdf_path, "PDF", resolution=300.0)
        print(f"Success! Margin-adjusted wraparound cover saved to {output_pdf_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find the front cover image at '{front_cover_path}'")

def flatten_kdp_manuscript(input_path, output_path, dpi=300):
    print(f"Rasterizing {input_path} at {dpi} DPI. This will take a minute for 50 pages...")
    
    try:
        # Convert all PDF pages to a list of PIL image objects
        pages = convert_from_path(input_path, dpi=dpi)
        
        if not pages:
            print("Error: No pages found in the source PDF.")
            return

        # Save the first image as a PDF and append the rest
        pages[0].save(
            output_path,
            "PDF",
            resolution=float(dpi),
            save_all=True,
            append_images=pages[1:]
        )
        print(f"Success! Flattened manuscript saved to {output_path}")
        
    except Exception as e:
        print(f"Conversion failed: {e}")

# Run the pipeline
# Replace 'front_cover.jpg' with your actual file name
create_wraparound_cover('front_cover.jpg', 'kdp_wraparound_cover.pdf', back_color='#1a0b2e')