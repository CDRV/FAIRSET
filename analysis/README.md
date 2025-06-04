# Sample analysis
**This section presents a short sample code for evaluating your algorithm on FAIRSET**

This analysis uses Mediapipe FaceMesh v2 along with FAIRSET to evaluate the algorithm on different demographics. To extract points from another algorithm, you'll need to create a json in the same format as `mediapipe_estimations.json`. For guidance a sample script was done for MediaPipe, see `./sample_extraction/mediapipe_extraction.py`. In order to run that script you'll need to instal the `face_landmarker.task` file from mediapipe's website.
## How-to guide
### 1. Setup your Python environment
The provided code was <u>tested on Python 3.11</u>, but it might still work on versions >= 3.9
- Python 3.11
- `python3 -m pip install -r analysis/requirements.txt`

### 2. Using and setting up scripts
You can then use and adapt the demographics_per_keypoint.py script. Using this script you can switch to a different demographic factor by replacing age by other factors. The configs for said analysis are done trough the configs.py file and the variables are as follows:
**configs.py variables:**

- **DATA**
  - `exclude_images_file`: Name of the text file listing images to exclude from analysis.
  - `annotations_file`: Path to the JSON file containing ground-truth annotations.
  - `estimations_file`: Path to the JSON file with keypoint estimations (e.g., from MediaPipe).

- **FILTERS**
  - `min_iod`: Minimum inter-ocular distance required for an image to be included. Set to -1 to disable this filter.
  - `max_nme`: Maximum normalized mean error allowed. Set to -1 to disable this filter.
  - `remove_statistical_bias`: If True, attempts to remove statistical bias from the dataset.

- **MEDIAPIPE**
  - `images_folder`: Path to the folder containing images for MediaPipe extraction.
  - `model_path`: Path to the MediaPipe model file used for face landmark detection.
  - `min_iou`: Minimum Intersection over Union required for associating detections.
  - `output_file`: Name of the output JSON file for MediaPipe extraction results.


### Script usage:
>usage: python3 scripts/demographics_per_keypoint.py [-h] [-a] [-p] [-d]
>
>**options:**
>- **-h, --help**            Show this help message and exit
>- **-f, --factor**          The demographic factor on which to run the analysis (default is 'age', options are 'age', 'sex' and 'skintone')
>- **-a, --all**             Display all results, including non-significant keypoints (default: True)
>- **-p, --prerequisites**   Runs and displays the prerequisites for the analysis
>- **-d, --descriptive**     Runs and displays the descriptive statistics for the analysis (default: True)
>
>**Example:**  
>`python3 analysis/scripts/demographics_per_keypoint.py -f sex -a -p -d`
