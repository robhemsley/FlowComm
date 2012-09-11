#include "flowclient.h"
#include "openhandler.h"
#include "copyhandler.h"
#include "watchhandler.h"
#include "filedownloader.h"

#include <QWebElement>
#include <QDebug>
#include <QByteArray>
#include <QFile>
#include <QFileInfo>

FlowClient::FlowClient(QWidget *parent, Qt::WFlags flags)
    : QWidget(parent, flags)
{
    ui.setupUi(this);
    ui.webView->settings()->setAttribute(QWebSettings::JavascriptEnabled, true);
    ui.webView->settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, true);
    ui.webView->settings()->setAttribute(QWebSettings::JavascriptCanAccessClipboard, true);
    ui.webView->setUrl(QUrl("http://flow.robhemsley.webfactional.com/static/test/flow_client_web.html"));

    connect(ui.webView->page()->mainFrame(), SIGNAL(loadFinished(bool)), this, SLOT(attachObject(bool)) );
}

void FlowClient::attachObject(bool ok)
{
    ui.webView->page()->mainFrame()->addToJavaScriptWindowObject(QString("openHandler"), new openHandler());
    ui.webView->page()->mainFrame()->addToJavaScriptWindowObject(QString("detailsHandler"), new openHandler());
    ui.webView->page()->mainFrame()->addToJavaScriptWindowObject(QString("copyHandler"), new copyHandler());
    ui.webView->page()->mainFrame()->addToJavaScriptWindowObject(QString("watchHandler"), new watchHandler());

    ui.webView->page()->mainFrame()->evaluateJavaScript(QString("function loadPlugins(){flowConnector.addHandler('OPEN', openHandler.process, true); flowConnector.addHandler('COPY', copyHandler.process, true); flowConnector.addHandler('WATCH', watchHandler.process, true); flowConnector.addHandler('DETAILS', detailsHandler.process, true);}"));
}

FlowClient::~FlowClient()
{
}
