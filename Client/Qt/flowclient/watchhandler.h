#ifndef WATCHHANDLER_H
#define WATCHHANDLER_H

#include <QObject>
#include "filedownloader.h"
#include <QUrl>

class watchHandler : public QObject
{
    Q_OBJECT
public:
    explicit watchHandler(QObject *parent = 0);
    const FileDownloader * m_pImgCtrl;
    QUrl * url;

signals:

public slots:
    void process(const QString &param);
    void dataDownloaded();
};

#endif // WATCHHANDLER_H
