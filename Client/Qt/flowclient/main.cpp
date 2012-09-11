

#include <QtGui/QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[])
{
    Q_INIT_RESOURCE(flowclient);
    QApplication app(argc, argv);
    MainWindow mainWindow;
    mainWindow.setWindowTitle("Flow - Client");
    mainWindow.show();
    return app.exec();
}
