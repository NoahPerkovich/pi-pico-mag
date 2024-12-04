import pcbnew

def resize_pads():
    board = pcbnew.GetBoard()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            # Set pad size to 2mm x 2mm (convert mm to nm)
            pad.SetSize(pcbnew.wxPoint(2000000, 2000000))  # Pad size in nanometers
            if pad.IsDrill():
                # Set drill size to 1.5mm (convert mm to nm)
                pad.SetDrill(1500000)  # Drill size in nanometers
    pcbnew.Refresh()

resize_pads()
