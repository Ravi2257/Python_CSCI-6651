import base64

# Path to your existing PPTX
pptx_file = "TechNova_Network_Design.pptx"

with open(pptx_file, "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

# Save the string to a text file (optional)
with open("ppt_base64.txt", "w") as f:
    f.write(encoded)

print("✅ Base64 string generated. Check ppt_base64.txt")

