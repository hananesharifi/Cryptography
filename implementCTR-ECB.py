from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

image_path = "your_image_path"
image = Image.open(image_path)
image_byte = image.tobytes()
key = get_random_bytes(32)

def framing(image_byte, framesize):
    frames = []
    for i in range(0, len(image_byte), framesize):
        frame = image_byte[i:i + framesize]
        frames.append(frame)
    return frames

image_frames = framing(image_byte, 1024)

def counter(index, nonce=b'\x00' * 8):
    return nonce + index.to_bytes(8, byteorder='big')

def xor_byte(sq1, sq2):
    min_len = min(len(sq1), len(sq2))
    return bytes(a ^ b for a, b in zip(sq1[:min_len], sq2[:min_len]))

def bit_to_color(bit):
    return (255, 255, 255) if bit == '1' else (0, 0, 0)

encrypted_frames = []
cipher = AES.new(key, AES.MODE_ECB)
counter_list = []
for i, frame in enumerate(image_frames):
    encrypted_frame = b''
    slice_frame = [frame[k:k + 16] for k in range(0, len(frame), 16)]

    for j, subframe in enumerate(slice_frame):
        ctr = counter(i * len(slice_frame) + j)
        encrypted_counter = cipher.encrypt(ctr)
        counter_list.append(encrypted_counter)
        encrypted_frame += xor_byte(encrypted_counter, subframe)

    encrypted_frames.append(encrypted_frame)

header_width = 64
new_height = len(encrypted_frames)
new_width = min(image.size[0], 342)

total_width = min(new_width + header_width, image.size[0] + header_width)
new_image = Image.new("RGB", (total_width, new_height))

for i, encrypted_frame in enumerate(encrypted_frames):
    counter_value = counter(i)
    bit_representation = ''.join(f'{byte:08b}' for byte in counter_value)
    header_pixels = [bit_to_color(bit) for bit in bit_representation]

    frame_with_header = list(encrypted_frame)
    if len(frame_with_header) % 3 != 0:
        frame_with_header.extend([0] * (3 - len(frame_with_header) % 3))
    row_pixels = [(frame_with_header[j], frame_with_header[j + 1], frame_with_header[j + 2]) for j in
                  range(0, len(frame_with_header), 3)]
    row_pixels = row_pixels[:new_width]

    combined_row = header_pixels + row_pixels

    combined_row = combined_row[:total_width]

    for x, pixel in enumerate(combined_row):
        new_image.putpixel((x, i), pixel)


new_image.show()
encrypted_image_byte = new_image.tobytes()

def separate_header(encrypted_frames, header_width, byte_per_pixel):
    headers = []
    datas = []
    header_length = 104

    for frame_enc in encrypted_frames:
        header = frame_enc[:header_length]
        data = frame_enc[header_length:]
        headers.append(header)
        datas.append(data)
    return headers, datas

byte_per_pixel = 3
encrypted_image_frame = framing(encrypted_image_byte, 1128)
header, encrypted_data = separate_header(encrypted_image_frame, header_width, byte_per_pixel)

#decryption
decrypted_frames = []
counter_index = 0
for i, encrypted_frame in enumerate(encrypted_frames):
    decrypted_frame = b''
    slice_frame_enc = [encrypted_frame[k:k + 16] for k in range(0, len(encrypted_frame), 16)]
    for j ,subframe_enc in enumerate(slice_frame_enc):
        encrypted_counter = counter_list[counter_index]
        counter_index += 1
        decrypted_frame += xor_byte(encrypted_counter,subframe_enc)
    decrypted_frames.append(decrypted_frame)


height = image.height
width = image.width

decrypted_byte = b''.join(decrypted_frames)
decrypted_image = Image.frombytes(image.mode ,image.size ,decrypted_byte)
decrypted_image.show()

if decrypted_image.tobytes() == image.tobytes():
    print("Decryption successful, images match!")
else:
    print("Decryption failed, images do not match.")
