from processor import process_image

print("Testing new processor logic locally...")
with open("sample_input.jpg", "rb") as f:
    input_bytes = f.read()

result_bytes = process_image(input_bytes)

with open("sample_watermark.jpg", "wb") as f:
    f.write(result_bytes)
print("Saved to sample_watermark.jpg")
