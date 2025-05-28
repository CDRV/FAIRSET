# FAIRSET
FAIRSET: an inclusive and balanced face landmark annotations dataset

# 1. Setup your Python environt
<u>Tested on Python 3.11</u>, but might still work on versions >= 3.9

# 2. Download the dataset
1) Request access to the DAD-3DHeads dataset: https://www.pinatafarm.com/research/dad-3dheads/dataset
2) Execute the download script
**Example:** `python3 ./download.py -o assets -d ~/DAD-3DHeadsDataset.zip`
&nbsp;
:warning: **If the script fails at some point, you can re-run it with the same arguments and it will continue downloading the missing images**

### Script usage:
>usage: python3 download.py -d DAD3dHEADS [-h] [-a] [-r] [-f] [-w WIDERFACE [WIDERFACE ...]] [-o OUTPUT]
>
>**options:**
>- **-h, --help**            Show this help message and exit
>- **-d** DAD3dHEADS, **--dad3d**  DAD3dHEADS
> Specify the location of the zip, or the download link, of the DAD-3DHeads dataset
> :warning: passing the direct download link instead of specifying the local zip might not work (missing header from AWS)
> - **-a, --alexa**          Download the Amazon Alexa demographics annotations for the WiderFace subset
>- **-r, --regenerate**      Regenerate the merged Amazon Alexa / Widerface annotations, if downloaded. Can be used with -a/--alexa
>- **-w** WIDERFACE [WIDERFACE ...], **--widerface** WIDERFACE [WIDERFACE ...]
> *(Optional)* Specify the location of the widerface zip(s). If no zip is specified, this script will try to fetch and extract the specific images from the remote zips on HuggingFace.
> :warning: HuggingFace might throttle you if you execute this script multiple times. In that case, download the zip(s) locally and pass zip the location(s) using -w.
>  **-f, --force**           Force download the dataset even if it seems present
>  **-o** OUTPUT, **--output** OUTPUT
> Directory to download the dataset to.
> This download script will create the following subdirectories:
>   - FAIRSET
>   - alexa (if -a was passed)


# References
> **Dad-3DHeads**
> T. Martyniuk, O. Kupyn, Y. Kurlyak, I. Krashenyi, J. Matas, and V. Sharmanska, “DAD-3DHeads: A Large-scale Dense, Accurate and Diverse Dataset for 3D Head Alignment from a Single Image,” in 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), New Orleans, LA, USA: IEEE, Jun. 2022, pp. 20910–20920. doi: 10.1109/CVPR52688.2022.02027.

> **Amazon Alexa Widerface Annotations**
> Y. Yang et al., “Enhancing Fairness in Face Detection in Computer Vision Systems by Demographic Bias Mitigation,” in Proceedings of the 2022 	AAAI/ACM Conference on AI, Ethics, and Society, Oxford United Kingdom: ACM, Jul. 2022, pp. 813–822. doi: 10.1145/3514094.3534153.


# License
FAIRSET is licensed under CC BY-NC-SA 4.0. View the LICENSE file or visit https://creativecommons.org/licenses/by-nc-sa/4.0/
