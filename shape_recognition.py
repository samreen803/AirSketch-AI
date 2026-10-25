import cv2
import numpy as np
import math


def distance(p1, p2):
    return math.sqrt(
        (p2[0] - p1[0]) ** 2 +
        (p2[1] - p1[1]) ** 2
    )


def path_length(points):
    total = 0

    for i in range(1, len(points)):
        total += distance(
            points[i - 1],
            points[i]
        )

    return total


def recognize_shape(points):

    # -----------------------------------------
    # Minimum points
    # -----------------------------------------

    if len(points) < 8:
        return "Unknown"


    # -----------------------------------------
    # Convert points into numpy array
    # -----------------------------------------

    pts = np.array(
        points,
        dtype=np.int32
    ).reshape((-1, 1, 2))


    # -----------------------------------------
    # Remove very close duplicate points
    # -----------------------------------------

    filtered_points = [points[0]]

    for p in points[1:]:

        if distance(
            filtered_points[-1],
            p
        ) > 3:

            filtered_points.append(p)


    if len(filtered_points) < 8:
        return "Unknown"


    pts = np.array(
        filtered_points,
        dtype=np.int32
    ).reshape((-1, 1, 2))


    # -----------------------------------------
    # Bounding box
    # -----------------------------------------

    x, y, w, h = cv2.boundingRect(pts)


    if w < 20 or h < 20:
        return "Unknown"


    # -----------------------------------------
    # Path length
    # -----------------------------------------

    total_length = path_length(
        filtered_points
    )


    # -----------------------------------------
    # Start and end distance
    # -----------------------------------------

    start_end_distance = distance(
        filtered_points[0],
        filtered_points[-1]
    )


    diagonal = math.sqrt(
        w * w + h * h
    )


    # -----------------------------------------
    # Check closed shape
    # -----------------------------------------

    # Increased tolerance because
    # hand drawing is not perfectly closed

    is_closed = (
        start_end_distance <
        diagonal * 0.40
    )


    # =========================================
    # LINE DETECTION
    # =========================================

    if not is_closed:

        if total_length > 0:

            straightness = (
                start_end_distance /
                total_length
            )

            # More tolerant than previous version

            if straightness > 0.70:

                return "Line"


    # =========================================
    # CLOSED SHAPE PROCESSING
    # =========================================

    if is_closed:

        # -------------------------------------
        # Close the contour
        # -------------------------------------

        closed_points = filtered_points.copy()

        closed_points.append(
            filtered_points[0]
        )


        contour = np.array(
            closed_points,
            dtype=np.int32
        ).reshape((-1, 1, 2))


        # -------------------------------------
        # Perimeter
        # -------------------------------------

        perimeter = cv2.arcLength(
            contour,
            True
        )


        if perimeter == 0:
            return "Unknown"


        # -------------------------------------
        # Polygon approximation
        # -------------------------------------

        epsilon = 0.02 * perimeter

        approx = cv2.approxPolyDP(
            contour,
            epsilon,
            True
        )


        corners = len(approx)


        # -------------------------------------
        # Area
        # -------------------------------------

        area = cv2.contourArea(
            contour
        )


        # =====================================
        # TRIANGLE
        # =====================================

        if corners == 3:

            return "Triangle"


        # =====================================
        # RECTANGLE
        # =====================================

        if corners == 4:

            # Calculate aspect ratio

            ratio = w / float(h)

            if 0.20 < ratio < 5.0:

                return "Rectangle"


        # =====================================
        # CIRCLE
        # =====================================

        if corners >= 5:

            circularity = (
                4 * math.pi * area
            ) / (
                perimeter * perimeter
            )


            # More tolerant threshold

            if circularity > 0.50:

                return "Circle"


    # =========================================
    # FALLBACK
    # =========================================

    return "Unknown"