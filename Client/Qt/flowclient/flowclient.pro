QT          +=  webkit network script
TARGET       =  flowclient
TEMPLATE     =  app
SOURCES     +=  main.cpp \
                mainwindow.cpp \
    openhandler.cpp \
    flowclient.cpp \
    watchhandler.cpp \
    filedownloader.cpp \
    copyhandler.cpp
HEADERS     +=  \
                mainwindow.h \
    openhandler.h \
    flowclient.h \
    watchhandler.h \
    filedownloader.h \
    copyhandler.h
FORMS        += \
    flowclient.ui
RESOURCES    += \
    flowclient.qrc

# install
target.path = $$[QT_INSTALL_EXAMPLES]/webkit/flowclient
sources.files = $$SOURCES $$HEADERS $$FORMS $$RESOURCES *.pro form.html images
sources.path = $$[QT_INSTALL_EXAMPLES]/webkit/flowclient
INSTALLS += target sources

symbian {
    TARGET.UID3 = 0xA000CF6D
    include($$PWD/../../symbianpkgrules.pri)
    TARGET.CAPABILITY = NetworkServices
}
maemo5: include($$PWD/../../maemo5pkgrules.pri)
contains(MEEGO_EDITION,harmattan): include($$PWD/../../harmattanpkgrules.pri)
