
from icalendar import vBinary

# 1. Create a small "image" payload (pretend PNG header + fake data)
original_bytes = (
    b"\x89PNG\r\n\x1a\n"  # PNG signature
    b"\x00\x00\x00\rIHDR"  # fake chunk
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
)

# 2. Wrap it into vBinary
vb = vBinary(original_bytes)

# 3. Serialize to iCal base64 form
ical_encoded = vb.to_ical()

# 4. Decode back using the library method
decoded_bytes = vBinary.from_ical(ical_encoded)

# 5. Save both to files for comparison
print("Original bytes:", original_bytes)
print("Decoded bytes:", decoded_bytes)

print("Match:", original_bytes == decoded_bytes)
