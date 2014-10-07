<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom">

<xsl:template match="/">
  <html>
  <body>
  <h1>Alert Feed</h1>
  <table border="1">
    <tr bgcolor="#9acd32">
      <th>Title</th>
      <th>Urgency</th>
    </tr>
    <xsl:for-each select="atom:feed">
    <tr>
      <td><xsl:value-of select="atom:feed/atom:entry:title"/></td>
    </tr>
    </xsl:for-each>
  </table>
  </body>
  </html>
</xsl:template>

</xsl:stylesheet>
