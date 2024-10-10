# PowerOutage2ATAK
Python app to scrape power outage data and visualize it in ATAK with dynamically updated, color-coded county polygons representing outage percentages.

Hosted at: [https://milton-tak.ddns.network](https://milton-tak.ddns.network) for the duration of the Milton Relief Efforts.

Repository: [PowerOutage2ATAK GitHub](https://github.com/joshuafuller/PowerOutage2ATAK/)

## Overview
This application gathers power outage data from public sources, processes the data to generate KML/KMZ files, and provides these files to ATAK users via a publicly accessible server. It represents outage severity using a color gradient that ranges from black (0% outages) to yellow (100% outages).

The KML/KMZ files are dynamically updated to ensure that ATAK users have the latest information available.

## Key Features
- **Dynamic Data Fetching**: Regularly scrapes outage data to maintain up-to-date visualizations.
- **Color-Coded Visualization**: Displays counties based on outage percentages, providing clear situational awareness.
- **ATAK Integration**: Generates KML/KMZ files accessible in ATAK/Wintak for real-time visual updates.

## Hosting and Access
- **Power Outage KML/KMZ Files**: Hosted at [https://milton-tak.ddns.network](https://milton-tak.ddns.network).
- **Milton Relief Efforts Page**: Detailed resources for the ongoing relief efforts can be found at [https://milton.takps.org/](https://milton.takps.org/).

## Milton Relief Efforts
The Milton Relief Efforts page contains detailed information on:
- **Hurricane Milton Response**: Coordination between federal, state, and local public safety organizations.
- **TAK Servers**: Information on available TAK servers for LEO, SOCOM, FLNG/FLSAR, and Florida public safety/responders.
- **Team Colors**: Guidelines for responder colors and callsigns.
- **Data Packages and Resources**: Including FEMA region data, fire and EMS station data, animal shelter data, and GeoJSONs for various Florida assets.
- **Alternate Comms**: Communication channels like Hurricane Watch Net frequencies.
- **TAK Server Plugins**: Plugins for FL511 and PulsePoint integration.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/joshuafuller/PowerOutage2ATAK/
   ```
2. Navigate to the project directory:
   ```bash
   cd PowerOutage2ATAK
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the script:
   ```bash
   python outage.py
   ```

## Acknowledgements
Thanks to the TAK Public Safety Slack #mapping channel for their support. Special thanks to Adrien Hoff and Joseph Elfelt for assisting with the finer points of KML generation.

## License
MIT License

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.
