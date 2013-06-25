'''OpenGL extension APPLE.fence

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_APPLE_fence'
_DEPRECATED = False
GL_DRAW_PIXELS_APPLE = constant.Constant( 'GL_DRAW_PIXELS_APPLE', 0x8A0A )
GL_FENCE_APPLE = constant.Constant( 'GL_FENCE_APPLE', 0x8A0B )
glGenFencesAPPLE = platform.createExtensionFunction( 
'glGenFencesAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLsizei,arrays.GLuintArray,),
doc='glGenFencesAPPLE(GLsizei(n), GLuintArray(fences)) -> None',
argNames=('n','fences',),
deprecated=_DEPRECATED,
)

glDeleteFencesAPPLE = platform.createExtensionFunction( 
'glDeleteFencesAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLsizei,arrays.GLuintArray,),
doc='glDeleteFencesAPPLE(GLsizei(n), GLuintArray(fences)) -> None',
argNames=('n','fences',),
deprecated=_DEPRECATED,
)

glSetFenceAPPLE = platform.createExtensionFunction( 
'glSetFenceAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,),
doc='glSetFenceAPPLE(GLuint(fence)) -> None',
argNames=('fence',),
deprecated=_DEPRECATED,
)

glIsFenceAPPLE = platform.createExtensionFunction( 
'glIsFenceAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=constants.GLboolean, 
argTypes=(constants.GLuint,),
doc='glIsFenceAPPLE(GLuint(fence)) -> constants.GLboolean',
argNames=('fence',),
deprecated=_DEPRECATED,
)

glTestFenceAPPLE = platform.createExtensionFunction( 
'glTestFenceAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=constants.GLboolean, 
argTypes=(constants.GLuint,),
doc='glTestFenceAPPLE(GLuint(fence)) -> constants.GLboolean',
argNames=('fence',),
deprecated=_DEPRECATED,
)

glFinishFenceAPPLE = platform.createExtensionFunction( 
'glFinishFenceAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,),
doc='glFinishFenceAPPLE(GLuint(fence)) -> None',
argNames=('fence',),
deprecated=_DEPRECATED,
)

glTestObjectAPPLE = platform.createExtensionFunction( 
'glTestObjectAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=constants.GLboolean, 
argTypes=(constants.GLenum,constants.GLuint,),
doc='glTestObjectAPPLE(GLenum(object), GLuint(name)) -> constants.GLboolean',
argNames=('object','name',),
deprecated=_DEPRECATED,
)

glFinishObjectAPPLE = platform.createExtensionFunction( 
'glFinishObjectAPPLE',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLenum,constants.GLint,),
doc='glFinishObjectAPPLE(GLenum(object), GLint(name)) -> None',
argNames=('object','name',),
deprecated=_DEPRECATED,
)


def glInitFenceAPPLE():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )