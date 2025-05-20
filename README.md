# VegeHub on Home Assistant

[![vegetronix_badge](https://img.shields.io/badge/VEGETRONIX-VEGEHUB-green)](https://www.vegetronix.com/Products/VG-HUB-RELAY/)

This is a [Home Assistant](https://www.home-assistant.io/) integration designed to interface with the [Vegetronix VegeHub](https://www.vegetronix.com/Products/VG-HUB-RELAY/). The version in this repository is intended to be accessed through [HACS](https://hacs.xyz/), but can also be **manually installed** into the `custom_components` folder of your Home Assistant server if desired.

This integration allows Home Assistant to automatically detect the presence of **VegeHub** devices on the local network, and to set them up to report their data to Home Assistant. It also allows Home Assistant to control actuators on the **VegeHub** (as long as the VegeHub is awake).

## Installation

### HACS Install

> [!NOTE]  
> The VegeHub integration has **not yet been merged** into HACS default integrations, so it does not currently show up in a search on HACS. Until it gets merged, the simplest way to install the VegeHub integration is as a **"Custom Repository"** on HACS. See [below](#custom-repository).

~~The **easiest** way to install this integration is through the Home Assistant Community Store ([HACS](https://hacs.xyz/)). Instructions for installing HACS can be found at [their website](https://hacs.xyz/docs/use/).~~

~~Once HACS is installed, open it in Home Assistant, and search for **VegeHub**. Click the VegeHub integration, and then click `install`.~~

### Custom Repository

If the integration does not show up in a HACS search, you can also add the integration as a `Custom repository` by clicking the three dots in the top right corner of HACS and selecting `Custom repositories`. There you can add the URL of this repository and set the `type` to `integration`, then HACS will add it to its list of integrations.

You can then search for, and install the integration.

### Manual Install

The integration can also be installed **manually** by copying the `vegehub` folder from the `custom_components` folder in this project into the `config->custom_components` folder in your Home Assistant instance. After the folder is copied into Home Assistant, Home Assistant **must be restarted** so that it can install the integration.

## Instructions

Once you have installed the integration and restarted Home Assistant, Home Assistant will start **monitoring** the local network for VegeHub devices. When it identifies one, it will present it in the `Discovered` devices in the `Settings->Devices & Services` menu. Click `Add`, and Home Assistant will contact the VegeHub, and set it up to report its data to Home Assistant.

> [!NOTE]  
> If your VegeHub does not show up in Home Assistant or setup fails, make sure the device is **awake**, and connected to the **same network** as Home Assistant. Also make sure that the VegeHub device is **awake** throughout the integration setup process.

Once setup is complete, the VegeHub device will be available in Home Assistant. If your device has **actuator outputs**, they will show up as switches, and if your device has **sensor inputs**, they will show up as sensors.

Once your device is set up in Home Assistant, you can go into the `Settings->Devices & Services` menu, and click on the VegeHub integration. With that open, you should see your device listed under `Integration entries`. Here you can click `configure` to select what **types of sensors** you are using on each input of your VegeHub, as well as the default actuator command duration, if your device has actuators.

If you click your device under `Integration entries`, you can use the pencil icon in the top bar to **change its name**, or click the individual sensors or switches to change their **names, icons, units of measurement**, etc.

> [!NOTE]  
> The VegeHub can only receive commands from Home Assistant if it is **awake**. If you try to flip a switch in Home Assistant and it does not work, make sure the VegeHub is **awake** to receive the command. If you want your VegeHub to always be able to receive commands, it will have to be configured to run on a `power adapter` rather than `batteries`. This setting can be changed in the VegeHub's **web interface**.

---

> [!IMPORTANT]  
> When the VegeHub gets set up, it points its data updates at your Home Assistant's **IP address**. If your Home Assistant instance **changes IP address**, the VegeHub will **no longer be able to send it data**, and you will have to do the setup process over again.  
> To avoid this, you should set a **static IP address** for your Home Assistant
