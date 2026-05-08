def euclidean_distance(x1, y1, x2, y2):
    """
    Calculates the straight line distance between two projected coordinates.
    Assumes inputs are in the same unit (e.g., meters) and returns that unit.
    """
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the hypotenuse using ** 0.5 for the square root
    distance = (dx**2 + dy**2) ** 0.5

    return distance


def calculate_distance(pt1, pt2, method="euclidean"):
    """
    Wrapper function to calculate distance between two points.

    Parameters
    ----------
    pt1: <list>
        A list containing [x, y] coordinates
    pt2: <list>
        A list containing [x, y] coordinates
    method: <str>
        The calculation method. Supported values: 'euclidean', 'manhattan'

    Returns
    -------
    <float>
        Computed distance.
    """
    if method == "euclidean":
        # Extract coordinates from the lists and pass to our dedicated function
        dist = euclidean_distance(pt1[0], pt1[1], pt2[0], pt2[1])

    elif method == "manhattan":
        dist = manhattan_distance(pt1[0], pt1[1], pt2[0], pt2[1])

    else:
        print("Method not supported yet.")
        dist = None

    return dist


def manhattan_distance(x1, y1, x2, y2):
    """
    Calculates the distance between two points in a grid-based path.

    Parameters
    ----------
    x1, y1: <float>
        Coordinates of the first point.
    x2, y2: <float>
        Coordinates of the second point.
    method: <str>
        The calculation method. Supported values: 'manhattan'
    
    Returns
    -------
    <float>
        Computed distance.
    """
    dx = ((x2 - x1)**2)**0.5
    dy = ((y2 - y1)**2)**0.5

    distance = dx + dy

    return distance