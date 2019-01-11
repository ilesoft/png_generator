"""
Implements solution to task defined in
https://gist.github.com/rantsi/8cb2d5b6df398977b69c84c98de2c2b0
:notes: Assignment is very clear but there is a problem in examples...
:author: Ilmari Marttila
:email: ilmari.marttila@student.tut.fi
:date: 13.12.2018
"""
from zlib import compress
from binascii import crc32
from os import getcwd, listdir


def png_creator(matrix):
    """
    Creates PNG picture according parameter matrix
    :param matrix: list of lists containing pixel values
    :return: bytes to write to image file
    """
    header = bytearray(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a')
    ihdr_chunk = bytearray(b'\x00\x00\x00\x0d'  # Always 13 bytes long chunk
                           b'\x49\x48\x44\x52'  # IHDR
                           b'\x00\x00\x00\00'   # Width of the picture
                           b'\x00\x00\x00\x00'  # Heigth of the picture
                           b'\x08'              # bit depth = 8 bit
                           b'\x00'              # color type = grayscale
                           b'\x00'              # compression method = 0
                           b'\x00'              # filttering = nope
                           b'\x00')             # interlace = nope ???

    # set heigth and width
    width = len(matrix[0])
    heigth = len(matrix)
    if width < 255 and heigth < 255:
        ihdr_chunk[11] = width
        ihdr_chunk[15] = heigth
    else:
        pass  # Doesn't work with bigger than 255x255
        return

    # Calculate crc-32
    ihdr_crc = crc32(ihdr_chunk[4:])
    ihdr_chunk.extend(ihdr_crc.to_bytes(4, byteorder='big'))
    # Now IHDR-chunk is ready

    pixels = bytearray(b'')
    for row in matrix:
        pixels.append(0)  # every row starts with \x00
        for pixel in row:
            pixels.append(pixel)

    idat_chunk_data = bytearray(b'\x08\x1d')
    # |CMF|FLG|: zlib first and second bytes
    # No need for real compression, so the zlib compression method code is 8
    # (deflate compression)
    idat_chunk_data.extend(compress(pixels, 0)[2:])

    # Set length of the chunk.
    idat_data_length = len(idat_chunk_data)
    idat_chunk = bytearray(idat_data_length.to_bytes(4, byteorder='big'))

    idat_chunk.extend(b'\x49\x44\x41\x54')  # IDAT

    # Attach the data
    idat_chunk.extend(idat_chunk_data)

    # Calculate crc-32
    idat_crc = crc32(idat_chunk[4:])
    idat_chunk.extend(idat_crc.to_bytes(4, byteorder='big'))
    # Now IDAT-chunk is ready

    # Add last chunk (IEND)
    iend_chunk = bytearray(b'\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82')

    # Cast to immutable type
    return bytes(header + ihdr_chunk + idat_chunk + iend_chunk)


def file_writer(image_bytes):
    """
    Writes image file to current working directory
    :param image_bytes:
    """
    while True:
        file_name = input("Give name for image file: ")

        if file_name[len(file_name)-4:] != ".png":
            file_name += ".png"

        # Check if file with same name already exists
        file_list = listdir(getcwd())
        if file_name in file_list:
            x = input("File with that name already exists.\n"
                      "Type Y to override or N to choose new file name: ")
            if x == 'Y' or x == 'y':
                break
        else:
            break
    with open(file_name, 'bw') as file:
        file.write(image_bytes)

    print("New PNG image is now in executing directory.")


def increase(original_matrix, multiplier):
    """
    Multiplyes the sie of the image by parameter multiplyer
    :param original_matrix:
    :param multiplier:
    :return: new, bigger matrix
    """
    new_matrix = []
    for original_row in original_matrix:
        new_row = []
        for pixel in original_row:
            # Multiply the count of pixels
            for _ in range(multiplier):
                new_row.append(pixel)

        for _ in range(multiplier):
            new_matrix.append(new_row)

    return new_matrix


def generate_image(seed_row, row_count):
    """
    Generates image based on seed row
    :param seed_row:
    :param row_count: How many lines will be generated
    :return: picture as a matrix
    """
    matrix = [[0]*len(seed_row) for _ in range(row_count + 1)]
    matrix[0] = seed_row

    rule_selection = input("Follow the rule defined by assignment or "
                           "example.\nInput A to assigment style or"
                           " empty to example style")

    for row in range(1, row_count + 1):
        for pixel in range(len(matrix[0])):
            # Pixels is the same color than the pixel above
            matrix[row][pixel] = matrix[row - 1][pixel]

            if rule_selection in ['a', 'A', "assigment"]:
                # Check the rule defined by assignment.
                # I can't believe that this is the way you want me to do this.

                same_color = 0
                different_colot = 0
                for x in [-2, -1, 1, 2]:
                    try:
                        if pixel + x < 0:
                            continue
                        if matrix[row-1][pixel + x] == matrix[row - 1][pixel]:
                            same_color += 1
                        else:
                            different_colot += 1
                    except IndexError:
                        pass
                if same_color > different_colot:
                    # Color have to change
                    if matrix[row - 1][pixel] == 1:
                        matrix[row][pixel] = 0
                    else:
                        matrix[row][pixel] = 1
            else:
                # Check the rule defined by examples
                # This makes sense much more than the other way to do this
                ones = 0
                zeros = 0
                for x in [-2, -1, 1, 2]:
                    try:
                        if pixel + x < 0:
                            continue
                        if matrix[row - 1][pixel + x] == 1:
                            ones += 1
                        else:
                            zeros += 1
                    except IndexError:
                        pass

                if ones > zeros:
                    # Color have to change
                    if matrix[row - 1][pixel] == 1:
                        matrix[row][pixel] = 0
                    else:
                        matrix[row][pixel] = 1

    # Remove the first row (seed)
    matrix.pop(0)

    # Edit values in matrix to represent 8-bit grayscale color
    for row in range(len(matrix)):
        for pixel in range(len(matrix[row])):
            if matrix[row][pixel] == 1:
                matrix[row][pixel] = 255

    return matrix


def check_input(input_list):
    """
    Checks (roughly) that input is valid. Can leak exception.
    :param input_list:
    :return: False if iput is invalid otherwise True
    """
    if len(input_list) > 256:
        print("Too long input")
        return False
    elif len(input_list) < 2:
        print("Too short input")
        return False
    elif input_list[0] < 0 or input_list[0] > 255:
        print("Too many rows to generate")
        return False
    # check right values
    for pixel in input_list[1:]:
        if int(pixel) != 0 and int(pixel) != 1:
            print("Wrong colors.")
            return False
    return True


def main():
    # Ask input
    print("Type input formatted as:\n"
          "<number_of_rows>;<color_of_pixel_1>;<color_of_pixel_2>"
          ";...;<color_of_pixel_n>;\n"
          "Use ones to represent white and zeros to black. "
          "Don't use another colors.\n"
          "Don't give reference data or number of pixels bigger "
          "than 255 pixels/rows.")
    while True:
        try:
            input_str = input('>')
            input_list = input_str.split(';')
            input_list = list(map(int, input_list))
            if check_input(input_list):
                break
        except TypeError as ex:
            print(ex)
        except ValueError as ex:
            print(ex)
        print("Try again")

    matrix = generate_image(input_list[1:], input_list[0])

    # Find out how big image should be
    multiplier = min(int(255 / input_list[0]), int(255 / len(input_list[1:])))

    # Make it as big as possible
    matrix2 = increase(matrix, multiplier)

    image_bytes = png_creator(matrix2)
    file_writer(image_bytes)


main()
