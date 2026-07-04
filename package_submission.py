import os
import zipfile
import shutil

def package():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    zip_filename = "kavalar_submission.zip"
    zip_path = os.path.join(root_dir, zip_filename)
    
    print("=========================================")
    print("Kavalar Submission Packaging Utility")
    print("=========================================")
    
    # 1. Copy the PDF write-up to root if it exists in backend
    pdf_src = os.path.join(root_dir, "backend", "solution_writeup.pdf")
    pdf_dest = os.path.join(root_dir, "solution_writeup.pdf")
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, pdf_dest)
        print("Copied solution_writeup.pdf to root.")
    else:
        print("WARNING: solution_writeup.pdf not found in backend folder.")
        
    # 2. Copy the browser demo video WebP to root if it exists
    video_src = r"C:\Users\hathi\.gemini\antigravity-ide\brain\1b9605dd-5359-4016-bd68-13f9ada2d199\kavalar_demo_flow_1783150017021.webp"
    video_dest = os.path.join(root_dir, "dashboard_demo.webp")
    if os.path.exists(video_src):
        shutil.copy2(video_src, video_dest)
        print("Copied dashboard_demo.webp to root.")
    else:
        print(f"WARNING: Video file not found at {video_src}")

    # Exclude list for zip packaging
    exclude_dirs = {
        ".git",
        "node_modules",
        ".next",
        "venv",
        "__pycache__",
        ".agents"
    }
    
    exclude_files = {
        zip_filename,
        "kavalar.db",
        "sentinel_ai.db",
        ".env"
    }
    
    print(f"Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Prune excluded directories in-place to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                # Skip any temporary files in scratch or system generated folders
                if ".system_generated" in root or ".gemini" in root:
                    continue
                    
                file_path = os.path.join(root, file)
                # Calculate relative path to store in zip
                rel_path = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, rel_path)
                
    print("-----------------------------------------")
    print(f"Packaging complete! Archive saved to:")
    print(f" -> {zip_path}")
    print(f"Size: {os.path.getsize(zip_path) / (1024 * 1024):.2f} MB")
    print("=========================================")

if __name__ == "__main__":
    package()
