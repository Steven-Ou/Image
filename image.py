from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter, PageObject
import os

def create_wraparound_cover(front_cover_path, output_pdf_path, back_color="#1a0b2e"):
    target_width = int(17.368 * 300)
    target_height = int(11.250 * 300)
    wraparound = Image.new('RGB', (target_width, target_height), back_color)

    try:
        front_cover = Image.open(front_cover_path).convert('RGB')
        front_width_original = int(8.625 * 300)
        
        safe_scale_factor = 0.92
        scaled_width = int(front_width_original * safe_scale_factor)
        scaled_height = int(target_height * safe_scale_factor)
        
        front_cover_safe = front_cover.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        padding_right = 110
        padding_top = (target_height - scaled_height) // 2 
        
        paste_x = target_width - scaled_width - padding_right
        paste_y = padding_top
        
        wraparound.paste(front_cover_safe, (paste_x, paste_y))
        wraparound.save(output_pdf_path, "PDF", resolution=300.0)
        print(f"Success! Wraparound cover saved to {output_pdf_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find '{front_cover_path}'")

def format_kdp_interior(input_pdf_path, output_pdf_path):
    print(f"Restructuring {input_pdf_path} for single-sided printing...")
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Skip index 0 (the cover) and insert blank pages behind all other pages
    for i in range(1, len(reader.pages)):
        content_page = reader.pages[i]
        writer.add_page(content_page)
        
        width = content_page.mediabox.width
        height = content_page.mediabox.height
        
        blank_page = PageObject.create_blank_page(width=width, height=height)
        writer.add_page(blank_page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    print(f"Success! Interior structured with blank pages: {output_pdf_path}")

def flatten_kdp_manuscript(input_path, output_path, dpi=300):
    print(f"Rasterizing {input_path} at {dpi} DPI to bypass font errors. This will take a minute...")
    try:
        pages = convert_from_path(input_path, dpi=dpi)
        if not pages:
            return
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

# --- MASTER PIPELINE EXECUTION ---

# 1. Generate the safe wraparound cover
create_wraparound_cover('front_cover.jpg', 'kdp_wraparound_cover_final.pdf')

# 2. Fix the interior structure (remove cover, add blank pages)
format_kdp_interior('interior_draft.pdf', 'interior_structured_temp.pdf')

# 3. Flatten the structured interior to bypass font errors
flatten_kdp_manuscript('interior_structured_temp.pdf', 'kdp_interior_final.pdf')

# 4. Clean up the temporary structured file
if os.path.exists('interior_structured_temp.pdf'):
    os.remove('interior_structured_temp.pdf')
    
print("Pipeline complete. Upload 'kdp_wraparound_cover_final.pdf' and 'kdp_interior_final.pdf' to KDP.")