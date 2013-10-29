import pygame
from PIL import Image
import multiprocessing
import sys
import os
import numpy as np
from bubo.util import bgr2rgb, numpy2iplimage
import cv2
import cv2.cv as cv
import signal
from time import sleep
import matplotlib.cm as cm 


# Window state
IMG = None
SCREEN = None
DRAWQUEUE = None
DRAWPROCESS = None

def imshow(im, title):
    figure()
    DRAWQUEUE.put(('_imshow', (im, title)))

def rectangle(bbox, color='green', caption=None, filled=False, linewidth=1):
    figure()
    DRAWQUEUE.put(('_rectangle', (bbox, color, caption, filled, linewidth)))

def ellipse(bbox, color='green', caption=None, filled=False, linewidth=1):
    figure()
    DRAWQUEUE.put(('_ellipse', (bbox, color, caption, filled, linewidth)))
    
def circle(center, radius, color, caption, filled=False, linewidth=1):
    figure()
    DRAWQUEUE.put(('_circle', (center, radius, color, caption, filled, linewidth)))


def frame(fr, im, color, caption):
    figure()
    DRAWQUEUE.put(('_frame', (fr, im, color, caption)))

def scatter(fr, im, color):
    figure()
    DRAWQUEUE.put(('_scatter', (fr, im, color)))

def figure(title=None):
    global DRAWPROCESS
    global DRAWQUEUE
    if (DRAWPROCESS is None) or (DRAWPROCESS.is_alive() == False):
        DRAWQUEUE = multiprocessing.Queue()
        p = multiprocessing.Process(target=_eventloop, args=(DRAWQUEUE,))
        #p.daemon = True
        p.start()        
        DRAWPROCESS = p
        
def close():
    global DRAWPROCESS
    if DRAWPROCESS is not None:
        pygame.display.quit()         
        DRAWPROCESS.terminate()
        DRAWPROCESS = None

def fullscreen():        
    figure()
    DRAWQUEUE.put(('_fullscreen', None))
    
    
def tracking(instream, framerate=None):
    # Initialize window
    pygame.init()
    (im, anno) = instream(async=True)[0]
    imsize = (im.get().shape[0], im.get().shape[1])
    screen = pygame.display.set_mode(imsize) 
    pygame.display.set_caption('tracking')
    imshown = im.url()
    img = pygame.image.load(im.url()) 

    # Initialize text
    font = pygame.font.SysFont(None, 12)

    # Update display
    for (im, anno) in instream(async=True):
        print anno        
        if anno['imurl'] != imshown:
            screen.blit(img, (0,0))
            if framerate is not None:
                pygame.time.wait(int(1000*(1.0/framerate)))
            pygame.display.flip() # update the display            
            img = pygame.image.load(im.url())             
            imshown = im.url()
        bbox = (anno['bbox_xmin'], anno['bbox_ymin'], anno['bbox_xmax']-anno['bbox_xmin'], anno['bbox_ymax']-anno['bbox_ymin'])
        pygame.draw.rect(img, (255,0,0), bbox, 1)

        text = font.render('%d' % anno['trackid'], 1, (0, 255, 0))
        textrect = text.get_rect()
        textrect.centerx = bbox[0] 
        textrect.centery = bbox[1]
        img.blit(text, textrect)
        
        #bbox(, imshape=(im.shape[0], im.shape[1]), bboxcaption=anno['trackid'])

def _pygame_to_cvimage(surface):
    """Convert a pygame surface into a cv image"""
    cv_image = cv.CreateImageHeader(surface.get_size(), cv.IPL_DEPTH_8U, 3)
    image_string = surface_to_string(surface)
    cv.SetData(cv_image, image_string)
    return cv_image
 
def _cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    image_rgb = cv.CreateMat(image.height, image.width, cv.CV_8UC3)
    cv.CvtColor(image, image_rgb, cv.CV_BGR2RGB)
    return pygame.image.frombuffer(image.tostring(), cv.GetSize(image_rgb), "RGB")
 
def _imshow(im, title=None, flip=True):
    global IMG
    global SCREEN
    
    if (type(im) is str) and os.path.isfile(im):
        imgfile = im
        im = Image.open(imgfile)  # do not load pixel buffer, just get size
        SCREEN = pygame.display.set_mode(im.size)         
        if title is not None:
            pygame.display.set_caption(title)
        IMG = pygame.image.load(imgfile) 
        SCREEN.blit(IMG, (0,0))
    else:
        if im.ndim == 2:
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)            
            im = im.transpose(1,0,2)            
        else:
            im = im.transpose(1,0,2)
            im = im[:, :, ::-1]  # bgr -> rgb
        SCREEN = pygame.display.set_mode((im.shape[0], im.shape[1])) 
        pygame.surfarray.blit_array(SCREEN, np.uint8(im))
        if title is not None:
            pygame.display.set_caption(title)        
    if flip:
        pygame.display.flip() # update the display                        
    
def _circle(pos, radius, color='green', caption=None, filled=False, linewidth=1):    
    global IMG
    global SCREEN
    
    if filled:
        linewidth = 0
    pygame.draw.circle(SCREEN, pygame.Color(color), pos, radius, linewidth)
    if caption is not None:
        font = pygame.font.SysFont(None, 12)
        text = font.render('%s' % caption, 1, (0, 255, 0))
        textrect = text.get_rect()
        textrect.centerx = pos[0] 
        textrect.centery = pos[1]
        SCREEN.blit(text, textrect)        
    pygame.display.flip() # update the display                

    
def _rectangle(bbox, color='green', caption=None, filled=False, linewidth=1):
    global IMG
    global SCREEN
    
    font = pygame.font.SysFont(None, 12)
    if filled:
        linewidth = 0
    pygame.draw.rect(SCREEN, pygame.Color(color), bbox, linewidth)
    #SCREEN.blit(IMG, (0,0))
    text = font.render('%s' % caption, 1, (0, 255, 0))
    textrect = text.get_rect()
    textrect.centerx = bbox[0] 
    textrect.centery = bbox[1]
    #IMG.blit(text, textrect)
    SCREEN.blit(text, textrect)    
    
    pygame.display.flip() # update the display                

def _ellipse(bbox, color='green', caption=None, filled=False, linewidth=1):
    global IMG
    global SCREEN
    
    font = pygame.font.SysFont(None, 12)
    if filled:
        linewidth = 0
    pygame.draw.ellipse(SCREEN, pygame.Color(color), bbox, linewidth)
    #SCREEN.blit(IMG, (0,0))
    text = font.render('%s' % caption, 1, (0, 255, 0))
    textrect = text.get_rect()
    textrect.centerx = bbox[0] 
    textrect.centery = bbox[1]
    #IMG.blit(text, textrect)
    SCREEN.blit(text, textrect)    
    
    pygame.display.flip() # update the display                

def _frame(fr, im=None, color='green', linewidth=1):
    global SCREEN

    _imshow(im, flip=False)
    for xysr in fr.transpose():
        bbox = (xysr[0], xysr[1], 10, 10)
        pygame.draw.rect(SCREEN, pygame.Color(color), bbox, 1)
        #pygame.draw.aalines(SCREEN, pygame.Color(color), True, pointlist, blend=1)  # for rotated square
    pygame.display.flip() # update the display                

def _scatter(fr, im=None, color='green', linewidth=1):
    global SCREEN

    n_frame = fr.shape[1]
    cmap = cm.get_cmap('jet', n_frame) 
    rgb = np.uint8(255*cmap(np.arange(n_frame)))
    _imshow(im, flip=False)
    for (i,xysr) in enumerate(fr.transpose()):
        pygame.draw.circle(SCREEN, pygame.Color(int(rgb[i,0]), int(rgb[i,1]), int(rgb[i,2]), int(rgb[i,3])), (int(xysr[0]), int(xysr[1])), 1, 1)        
    pygame.display.flip() # update the display                

    
def _fullscreen():
    pygame.display.toggle_fullscreen()  # doesn't work


def _eventloop(drawqueue):
    pygame.init()
    pygame.display.set_icon(pygame.image.load('/Users/jebyrne/dev/bubo/data/visym_owl.png'))        

    # Ignore keyboard interrupt (passthrough to parent)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
        
    # Initialize display
    global SCREEN
    SCREEN = pygame.display.set_mode((320, 240))         
    pygame.display.set_caption('Figure')
    pygame.display.flip() # update the display                
    
    # Event loop
    Clock = pygame.time.Clock()
    done = False
    while not done:
        # GUI events
        Clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    #done = True 
                    done = False

        # Drawing events
        if not drawqueue.empty():
            # BUG: filling queue may be faster than emptying, so real time has lag, 
            # wait until queue is empty to continue on put, or change to pipe?
            (funcname, args) = drawqueue.get()
            func = globals()[funcname]
            if args is not None:
                func(*args)
            else:
                func()
            
    sys.stdout.flush()
    pygame.quit()
    sys.exit()
    

