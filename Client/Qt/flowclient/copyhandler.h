#ifndef COPYHANDLER_H
#define COPYHANDLER_H

#include "filedownloader.h"
#include <QUrl>

class copyHandler : public QObject
{
    Q_OBJECT
public:
    explicit copyHandler(QObject *parent = 0);
    const FileDownloader * m_pImgCtrl;
    QUrl * url;

signals:

public slots:
    void process(const QString &param);
    void dataDownloaded();
};

#endif // COPYHANDLER_H
