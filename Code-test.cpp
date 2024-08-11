#include <opencv2/opencv.hpp>

using namespace cv;

int main() {
    VideoCapture cap(0); // 0 pour la caméra par défaut

    if (!cap.isOpened()) {
        std::cout << "Erreur lors de l'ouverture de la caméra" << std::endl;
        return -1;
    }

    while (true) {
        Mat frame;
        cap >> frame;

        // Traiter l'image (affichage, enregistrement, etc.)
        imshow("Video", frame);

        if (waitKey(30) >= 0)
            break;
    }

    cap.release();
    return 0;
}
