#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import math
from contextlib import contextmanager

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

from evdev import InputDevice, categorize, ecodes, list_devices


devices = [InputDevice(path) for path in list_devices()]
for device in devices:
	if device.name.find('PLAYSTATION(R)3') != -1 and device.name.find('Motion')== -1:
		print(device.path, device.name, device.phys)
		controllerName = 'PS3_controller'
		deviceID = device.path
	elif device.name.find('Sony Computer Entertainment Wireless') != -1 and device.name.find('Motion')== -1 and device.name.find('Touch')== -1 or device.name.find('Wireless Controller')!=-1 and device.name.find('Motion')== -1 and device.name.find('Touch')== -1:
		controllerName = 'PS4_controller'
		deviceID = device.path
	elif device.name.find('Xbox 360') != -1 :
		controllerName = 'Xbox360_controller'
		deviceID = device.path
	elif device.name.find('Microsoft') != -1 :
		controllerName = 'XboxOne_controller'
		deviceID = device.path

gamepad = InputDevice(deviceID)

if (controllerName == 'PS3_controller'):
	print('ps3 configuration loaded')
	#button codes
	aBtn = 305
	bBtn = 304
	xBtn = 307
	yBtn = 308

	up = 544
	down = 545
	left = 546
	right = 547

	d_pad = 999999

	start = 315
	select = 314

	l1Trig = 310
	r1Trig = 311
	l2Trig = 312
	r2Trig = 313

	lBtn = 317
	rBtn = 318

	homeBtn = 316

	ABS_scale = 255
	ABS_translate = 0

elif (controllerName == 'PS4_controller'):
	print('ps4 configuration loaded')
	#button codes
	aBtn = 305
	bBtn = 304
	xBtn = 307
	yBtn = 308

	up = 999999
	down = 999999
	left = 999999
	right = 999999

	d_pad = 'ps4'

	start = 315
	select = 314

	l1Trig = 310
	r1Trig = 311
	l2Trig = 312
	r2Trig = 313

	lBtn = 317
	rBtn = 318

	homeBtn = 316

	ABS_scale = 255
	ABS_translate = 0

elif (controllerName == 'Xbox360_controller'):
	print('xbox360 configuration loaded')
	#button codes
	aBtn = 305
	bBtn = 304
	xBtn = 308
	yBtn = 307

	up = 999999
	down = 999999
	left = 999999
	right = 999999

	d_pad = 'ps4'

	start = 315
	select = 314

	l1Trig = 310
	r1Trig = 311
	l2Trig = 99999
	r2Trig = 99999

	lBtn = 317
	rBtn = 318

	homeBtn = 316

	ABS_scale = 128*255*2
	ABS_translate = 32768

elif (controllerName == 'XboxOne_controller'):
	print('xboxOne configuration loaded')
	#button codes
	aBtn = 304
	bBtn = 305
	xBtn = 308
	yBtn = 307

	up = 999999
	down = 999999
	left = 999999
	right = 999999

	d_pad = 'ps4'

	start = 315
	select = 314

	l1Trig = 310
	r1Trig = 311
	l2Trig = 99999
	r2Trig = 99999

	lBtn = 317
	rBtn = 318

	homeBtn = 316

	ABS_scale = 128*255*2
	ABS_translate = 32768


logger = logging.getLogger(__name__)

def lerp(a, b, percentage):
    return (percentage * a) + ((1 - percentage) * b)


async def controller_inputs(controller_state):

	button_zl_pressed = False
	button_zr_pressed = False


	stickL = controller_state.l_stick_state
	calibrationL = stickL.get_calibration()
	stickR = controller_state.r_stick_state
	calibrationR = stickR.get_calibration()

	maxUp_L = calibrationL.v_center + calibrationL.v_max_above_center
	maxDown_L = calibrationL.v_center - calibrationL.v_max_below_center
	maxRight_L = calibrationL.h_center + calibrationL.h_max_above_center
	maxLeft_L = calibrationL.h_center - calibrationL.h_max_below_center

	maxUp_R = calibrationR.v_center + calibrationR.v_max_above_center
	maxDown_R = calibrationR.v_center - calibrationR.v_max_below_center
	maxRight_R = calibrationR.h_center + calibrationR.h_max_above_center
	maxLeft_R = calibrationR.h_center - calibrationR.h_max_below_center

	print('ready')

	for event in gamepad.read_loop():
		if event.type==ecodes.EV_KEY:
			if event.value ==1:
				if event.code == xBtn:
					await button_push(controller_state, 'x')
				elif event.code == yBtn:
					await button_push(controller_state, 'y')
				elif event.code == aBtn:
					await button_push(controller_state, 'a')
				elif event.code == bBtn:
					await button_push(controller_state, 'b')
				elif event.code == up:
					await button_push(controller_state, 'up')
				elif event.code == down:
					await button_push(controller_state, 'down')
				elif event.code == left:
					await button_push(controller_state, 'left')
				elif event.code == right:
					await button_push(controller_state, 'right')
				elif event.code == start:
					await button_push(controller_state, 'plus')
				elif event.code == select:
					await button_push(controller_state, 'minus')
				elif event.code == l1Trig:
					await button_push(controller_state, 'l')
				elif event.code == r1Trig:
					await button_push(controller_state, 'r')
				elif event.code == l2Trig:
					await button_push(controller_state, 'zl')
				elif event.code == r2Trig:
					await button_push(controller_state, 'zr')
				elif event.code == lBtn:
					await button_push(controller_state, 'l_stick')
				elif event.code == rBtn:
					await button_push(controller_state, 'r_stick')
				elif event.code == homeBtn:
					await button_push(controller_state, 'home')
			elif event.value == 0:
				if event.code == xBtn:
					await button_release(controller_state, 'x')
				elif event.code == yBtn:
					await button_release(controller_state, 'y')
				elif event.code == aBtn:
					await button_release(controller_state, 'a')
				elif event.code == bBtn:
					await button_release(controller_state, 'b')
				elif event.code == up:
					await button_release(controller_state, 'up')
				elif event.code == down:
					await button_release(controller_state, 'down')
				elif event.code == left:
					await button_release(controller_state, 'left')
				elif event.code == right:
					await button_release(controller_state, 'right')
				elif event.code == start:
					await button_release(controller_state, 'plus')
				elif event.code == select:
					await button_release(controller_state, 'minus')
				elif event.code == l1Trig:
					await button_release(controller_state, 'l')
				elif event.code == r1Trig:
					await button_release(controller_state, 'r')
				elif event.code == l2Trig:
					await button_release(controller_state, 'zl')
				elif event.code == r2Trig:
					await button_release(controller_state, 'zr')
				elif event.code == lBtn:
					await button_release(controller_state, 'l_stick')
				elif event.code == rBtn:
					await button_release(controller_state, 'r_stick')
				elif event.code == homeBtn:
					await button_release(controller_state, 'home')
		elif event.type==ecodes.EV_ABS:
				if event.code == 1:
					# vertical L
					percentLv = (event.value + ABS_translate) / ABS_scale
					v_value_L = int(lerp(maxDown_L, maxUp_L, percentLv))
					stickL.set_v(v_value_L)
					# await controller_state.send()
					await asyncio.sleep(0)
				elif event.code == 0:
					# horizontal L
					percentLh = (event.value + ABS_translate) / ABS_scale
					h_value_L = int(lerp(maxRight_L, maxLeft_L, percentLh))
					stickL.set_h(h_value_L)
					# await controller_state.send()
					await asyncio.sleep(0)
				elif event.code == 4:
					# vertical R
					percentRv = (event.value + ABS_translate) / ABS_scale
					v_value_R = int(lerp(maxDown_R, maxUp_R, percentRv))
					stickR.set_v(v_value_R)
					# await controller_state.send()
					await asyncio.sleep(0)
				elif event.code == 3:
					# horizontal R
					percentRh = (event.value + ABS_translate) / ABS_scale
					h_value_R = int(lerp(maxRight_R, maxLeft_R, percentRh))
					stickR.set_h(h_value_R)
					# await controller_state.send()
					await asyncio.sleep(0)
				elif event.code == 2:
					# xbox360 LT
					if event.value > 0 and button_zl_pressed == False:
						await button_push(controller_state, 'zl')
						button_zl_pressed = True
					elif event.value == 0 and button_zl_pressed == True :
						await button_release(controller_state, 'zl')
						button_zl_pressed = False
					# await controller_state.send()
					await asyncio.sleep(0)
				elif event.code == 5:
					# xbox360 RT
					if event.value > 0 and button_zr_pressed == False:
						await button_push(controller_state, 'zr')
						button_zr_pressed = True
					elif event.value == 0 and button_zr_pressed == True :
						await button_release(controller_state, 'zr')
						button_zr_pressed = False
					# await controller_state.send()
					await asyncio.sleep(0)
				if d_pad=='ps4':
					if event.code==17:
						if event.value==-1:
							await button_push(controller_state, 'up')
						elif event.value==1:
							await button_push(controller_state, 'down')
						elif event.value==0:
							await button_release(controller_state, 'down')
							await button_release(controller_state, 'up')
					elif event.code==16:
						if event.value==-1:
							await button_push(controller_state, 'left')
						elif event.value==1:
							await button_push(controller_state, 'right')
						elif event.value==0:
							await button_release(controller_state, 'left')
							await button_release(controller_state, 'right')




async def _main(controller, reconnect_bt_addr=None, capture_file=None, spi_flash=None, device_id=None):
    factory = controller_protocol_factory(controller, spi_flash=spi_flash)
    ctl_psm, itr_psm = 17, 19
    transport, protocol = await create_hid_server(factory, reconnect_bt_addr=reconnect_bt_addr, ctl_psm=ctl_psm,
                                                  itr_psm=itr_psm, capture_file=capture_file, device_id=device_id)

    controller_state = protocol.get_controller_state()

    controller_state.l_stick_state.set_center()
    controller_state.r_stick_state.set_center()

    if controller_state.get_controller() != Controller.PRO_CONTROLLER:
    	raise ValueError('This script only works with the Pro Controller!')


    await controller_state.connect()

    await controller_inputs(controller_state)


    logger.info('Stopping communication...')
    await transport.close()


if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    #log.configure(console_level=logging.ERROR)
    log.configure()

    parser = argparse.ArgumentParser()
    parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
    parser.add_argument('-l', '--log')
    parser.add_argument('-d', '--device_id')
    parser.add_argument('--spi_flash')
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address, for reconnecting as an already paired controller')
    args = parser.parse_args()

    if args.controller == 'JOYCON_R':
        controller = Controller.JOYCON_R
    elif args.controller == 'JOYCON_L':
        controller = Controller.JOYCON_L
    elif args.controller == 'PRO_CONTROLLER':
        controller = Controller.PRO_CONTROLLER
    else:
        raise ValueError(f'Unknown controller "{args.controller}".')

    spi_flash = None
    if args.spi_flash:
        with open(args.spi_flash, 'rb') as spi_flash_file:
            spi_flash = FlashMemory(spi_flash_file.read())
            print(spi_flash.get_factory_l_stick_calibration())
            print(spi_flash.get_factory_r_stick_calibration())

    with utils.get_output(path=args.log, default=None) as capture_file:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            _main(controller,
                  reconnect_bt_addr=args.reconnect_bt_addr,
                  capture_file=capture_file,
                  spi_flash=spi_flash,
                  device_id=args.device_id
                  )
        )
