# FOR TESTING PURPOSES ONLY
from dyio import DyIO
import bowler

func = "_rev"
args = []

dyio = DyIO("COM3","74:F7:26:80:00:4F")
datagram = bowler.build_datagram(dyio.mac,func,args=args)
bowler.send_datagram(dyio.port,datagram)
func,args,priority,state,async,dir,encrypted = bowler.receive_datagram(dyio.port)

for byte in args:
	print hex(byte)
