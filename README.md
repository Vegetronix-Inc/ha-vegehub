# VegeHub on HACS

[![vegetronix_badge](https://img.shields.io/badge/VEGETRONIX-VEGEHUB-green)](https://www.vegetronix.com/Products/VG-HUB-RELAY/)

This is a [Home Assistant](https://www.home-assistant.io/) integration designed to interface with the [Vegetronix VegeHub](https://www.vegetronix.com/Products/VG-HUB-RELAY/). The version in this repository is intended to be accessed through [HACS](https://hacs.xyz/), but can also be manually installed into the `custom_components` folder of your Home Assistant server if desired.

This integration allows Home Assistant to automatically detect the presence of VegeHub devices on the local network, and to set them up to report their data to Home Assistant. It also allows Home Assistant to control actuators on the VegeHub (as long as the VegeHub is awake).

## Installation

### HACS

The easiest way to install this integration is through the Home Assistant Community Store [HACS](https://hacs.xyz/). Instructions for installing HACS can be found at their [website](https://hacs.xyz/docs/use/).

Once HACS is installed, open it in Home Assistant, and search for VegeHub. Click the VegeHub integration, and then click `install`.

If the integration does not show up in a HACS search, you can also add this repository as a `Custom repository` buy clicking the three dots in the top right corner of HACS and selecting `Custom repositories`. There you can add the URL of this repository and set the `type` to `integration`, and HACS will add it to its list of integrations.

### Manual

The integration can also be manually by copying the `vegehub` folder from the `custom_components` folder in this project into the `config->custom_components` folder in your Home Assistant instance. After the folder is copied into Home Assistant, Home Assistant should be restarted so that it can install the integration.

## Instructions

Once you have installed the integration, Home Assistant will start watching the local network for VegeHub devices. Whe it identifies one, it will present it in the `Discovered` devices in the `Settings->Devices & Services` menu. Click `Add`, and Home Assistant will contact the VegeHub, and set it up to report its data to Home Assistant.

If your VegeHub does not show up in Home Assistant, make sure the device is awake, and connected to the same network as Home Assistant. Also make sure that the VegeHub device is awake throughout the integration setup process.

> [!IMPORTANT]  
> When the VegeHub gets set up, it points its data updates at your Home Assistant's IP address. If your Home Assistant instance changes IP address, the VegeHub will no longer be able to send it data, and you will have to do the setup process over again.

Once setup is complete, the VegeHub device will be available in Home Assistant. If your device has actuators, they will show up as switches, and if your device has sensor inputs, they will show up as sensors.

With a configured device in Home Assistant, you can go into the `Settings->Devices & Services` menu, and click on the VegeHub integration. With that open, you should see your device listed under `Integration entries`. Here you can click `configure` to select what kinds of sensors you are using on each channel of your VegeHub, as well as the default actuator command duration, if your device has actuators.

If you click your device under `Integration entries`, you can use the pencil icon in the top bar to change its name, or click the individual sensors or switches to change their names, icons, units of measurement, etc.
