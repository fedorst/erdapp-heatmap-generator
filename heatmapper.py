"""Generate heatmap."""
import topo
import os.path
from PIL import Image, ImageDraw


def generate_map(topo_data, width, height, filename, bw):
    """
    Generate (heat)map into an image file.

    topo_data comes from topo module. The data is a list
    where every element contains latitude, longitude and altitude (in meters).
    The function should treat coordinates as regular y and x (flat world).
    The image should fill the whole width, height. Every "point" in the data
    should be represented as a rectangle on the image.

    For example, if topo_data has 12 elements (latitude, longitude, altitude):
    10, 10, 1
    10, 12, 1
    10, 14, 2
    12, 10, 1
    12, 12, 3
    12, 14, 1
    14, 10, 6
    14, 12, 9
    14, 14, 12
    16, 10, 1
    16, 12, 1
    16, 14, 3
    and the width = 100, height = 100
    then the first line in data should be represented as a rectangle (0, 0) - (33, 25)
    (x1, y1) - (x2, y2).
    The height is divided into 4, each "point" is 100/4 = 25 pixels high,
    the width is divided into 3, each "point" is 100/3 = 33 pixels wide.
    :param bw: Boolean whether the generated map should be black and white
    :param topo_data: list of topography data (from topo module)
    :param width: width of the image
    :param height: height of the image
    :param filename: the file to be written
    :return: True if everything ok, False otherwise
    """
    # count unique latitudes
    i = 0
    same = 0
    orig = topo_data[0][0]
    while topo_data[i][0] == orig:
        i += 1
        same += 1
        continue
    print("width units:", same)
    print("height units:", len(topo_data) / same)
    pixelwidth = width / same
    pixelheight = height / (len(topo_data) / same)
    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)
    for i in range(int(len(topo_data) / same)):
        for j in range(int(same)):
            value = i * same + j
            print(value, i, j)
            draw.rectangle([j * pixelwidth, i * pixelheight, (j + 1) * pixelwidth, (i + 1) * pixelheight], fill=get_color(topo_data[int(value)][2], bw))
    im.save(filename)
    return True


def get_color(topo_value: int, bw: bool):
    """
    Get color according to a gradient from the topo_value.

    :param topo_value:
    :return: RGB tuple of colors.
    """
    # if type(topo_value) == type(None):
    #     return(0, 0, 0)
    # -20 to +256
    if bw:
        if topo_value < 0:
            bwValue = 64 - abs(topo_value)
            return (bwValue, bwValue, bwValue)
        else:
            bwValue = 64 + abs(topo_value)
            return (bwValue, bwValue, bwValue)
    if topo_value < 0:        # 0,0 55 - 255 (diff = 200), min limit = -10000, therefore 50m per 1 or -1 * 10000/200
        return (0, 0, int(255 + topo_value / 60))
    elif topo_value == 0:
        return (0, 0, 0)
    elif topo_value < 150:      # 0-50, 195 - 255, 150 - 0 (diff = 60, -150), max limit = 150
        return (int(topo_value / 3), int(195 + 0.4 * topo_value), int(150 - topo_value))  # end:0, 255, 0
    elif topo_value < 650:
        return (int(0.3 * (topo_value - 500)), 255, 0)   # 50 - 200, 255, 0, 150 to 650, diff - 500
    elif topo_value < 1250:                         # 200, 255 - 155, 0 - 50. 650 0.08333333333
        return (200, int(255 - (topo_value - 650) / 6), int(0.083333 * (topo_value - 650)))
    else:                                           # 200-160, 155-75, 50-20, 1250 to 8000, diff 6750
        return (int(200 - (topo_value - 1250) * 0.005926), int(155 - (topo_value - 1250) * 0.011852), int(50 - (topo_value - 1250) * 0.00444))


def generate_map_with_coordinates(topo_params, image_width, image_height, filename, bw=False):
    """
    Given the topo parameters and image parameters, generate map into a file.

    topo_parameters = (min_latitude, max_latitude, latitude_stride, min_longitude, max_longitude, longitude_stride)
    In the case where latitude_stride and/or longitude_stride are 0,
    you have to calculate step yourself, based on the image parameters.
    For example, if image size is 10 x 10, there is no point to query more than 10 x 10 topological points.
    Hint: check the website, there you see "size" for both latitude and longitude.
    Also, read about "stride" (the question mark behind stride in the form).

    Optional (recommended) caching:
    if all the topo params are calculated (or given), then it would be wise
    to cache the query results. One implementation could be as follows:
    filename = topo_57-60-3_22-28-1.json
    (where 57 = min_lat, 60 = max_lat, 3 latitude stride etc)
     if file exists:
         topo.read_json_from_file(file)
     else:
         result = topo.read_json_from_web(...)
         with open(filename, 'w'):
             f.write(result)

     ... do the rest


    :param bw: Boolean.
    :param topo_params: tuple with parameters for topo query
    :param image_width: image width in pixels
    :param image_height: image height in pixels
    :param filename: filename to store the image
    :return: True, if everything ok, False otherwise
    """
    if topo_params[2] == 0:
        newstep_ver = int(120 / (image_height / (topo_params[1] - topo_params[0])))
    else:
        newstep_ver = topo_params[2]
    if topo_params[5] == 0:
        newstep_hor = int(120 / (image_width / (topo_params[4] - topo_params[3])))
    else:
        newstep_hor = topo_params[5]

    pathstring = "topo_" + str(topo_params[0]) + "-" + str(topo_params[1]) + "-" + str(newstep_ver) + "_" + str(topo_params[3]) + "-" + str(topo_params[4]) + "-" + str(newstep_hor) + ".json"
    if os.path.isfile(pathstring):
        topo_data = topo.read_json_from_file(pathstring)
    else:
        topo_data = topo.read_json_from_web(topo_params[0], topo_params[1], newstep_ver, topo_params[3], topo_params[4], newstep_hor)
        with open(pathstring, 'w') as f:
            f.write(topo_data)

    topo_data = topo.get_topo_data_from_string(topo_data)
    generate_map(topo_data, image_width, image_height, filename, bw)
    return True


if __name__ == '__main__':
    # topo_data = topo.get_topo_data_from_string(topo.read_json_from_web(57, 61, 1, 23, 27, 1))

    # print(topo_data)
    # print(len(topo_data))
    # generate_map(topo_data, 400, 400, "mymap.png")

    # generate_map_with_coordinates((56, 62, 1, 20, 30, 1), 1500, 1000, "eestiBW.png", bw=True)
    generate_map_with_coordinates((57, 60, 1, 24, 27, 1), 2400, 2400, "lounaEestiBW.png", bw=True)
    # generate_map_with_coordinates((30, 80, 8, -25, 70, 8), 1800, 1200, "europe.png")
    # generate_map_with_coordinates((-89, 90, 15, -179, 179, 15), 2880, 1440, "world.png")
