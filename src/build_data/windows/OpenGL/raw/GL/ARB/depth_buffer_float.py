'''OpenGL extension ARB.depth_buffer_float

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_ARB_depth_buffer_float'
_DEPRECATED = False
GL_DEPTH_COMPONENT32F = constant.Constant( 'GL_DEPTH_COMPONENT32F', 0x8CAC )
GL_DEPTH32F_STENCIL8 = constant.Constant( 'GL_DEPTH32F_STENCIL8', 0x8CAD )
GL_FLOAT_32_UNSIGNED_INT_24_8_REV = constant.Constant( 'GL_FLOAT_32_UNSIGNED_INT_24_8_REV', 0x8DAD )


def glInitDepthBufferFloatARB():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
