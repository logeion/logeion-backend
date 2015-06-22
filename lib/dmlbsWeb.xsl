<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"
	version="2.0">
	
	<xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
		<xd:desc>
			<xd:p><xd:b>Created on:</xd:b> June 11, 2015</xd:p>
			<xd:p><xd:b>Author:</xd:b> alexlee</xd:p>
			<xd:p>Try to fix up DMLBS source XML for presentation in Logeion.</xd:p>
		</xd:desc>
	</xd:doc>
	
	<!--
		addinfo
	
		addinfo:before {content:"  "}
		addinfo:after {content:"."}
		q2>addinfo:before {content:"("}
		q2>addinfo:after {content:") ";font-weight:normal}
	-->
	<xsl:template match="addinfo">
		<!-- before -->
		<xsl:choose>
			<xsl:when test="parent::q2">
				<xsl:text>(</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text> </xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<xsl:choose>
			<xsl:when test="parent::q2">
				<xsl:text>) </xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>.</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- 
		altplace
		
		altplace:before {content:" (=\2009";font-style:normal}
		altplace:after {content:")";font-style:normal}
	-->
	<xsl:template match="altplace">
		<xsl:text> (=&#x2009;</xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>)</xsl:text>
	</xsl:template>
	
	<!--
		entry
		
		UNTESTED
		
		entry[crossref=true]+entry[crossref=true]:before {content:"\2003\2003"}
	-->
	<xsl:template match="entry[@crossref='true']">
		<xsl:if test="preceding-sibling::*[1][self::entry[@crossref='true']]">
			<xsl:text>&#x2003;&#x2003;</xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		et
		Surround with brackets and leading whitespace.
		
		l+et:before {content:" ["}
		et:before {content:"["}
		et:after {content:"]"}
	-->
	<xsl:template match="et">
		<xsl:text>
[</xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>]</xsl:text>
	</xsl:template>
	
	<!--
		fl, child of s1
		
		s1>fl:before {content:""}
		s1>fl[query=true]:before {content:"?\00a0";font-style:normal}
		s1>fl:after {content:"f.\00a0l.";font-style:italic}
	-->
	<xsl:template match="fl[parent::s1]">
		<!-- before -->
		<xsl:if test="@query='true'">
			<xsl:text>?&#x00a0;</xsl:text>
		</xsl:if>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<span class="italic"><xsl:text>f.&#x00a0;l.</xsl:text></span>
	</xsl:template>
	
	<!--
		fl, child of def
		
		def>fl:before {content:", or "}
		def>fl[query=true]:before {content:", or ?\00a0";font-style:normal}
		def>fl:after {content:"f.\00a0l";font-style:italic}
	-->
	<xsl:template match="fl[parent::def]">
		<!-- before -->
		<xsl:choose>
			<xsl:when test="@query='true'">
				<xsl:text>, or ?&#x00a0;</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>, or </xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<span class="italic"><xsl:text>f.&#x00a0;l</xsl:text></span>
	</xsl:template>
	
	<!-- 
		fraction
		
		Originally the slash was U+2044, but we'll just use U+002f '/'.
	
		fraction:before {content:attr(numerator);vertical-align:top;font-size:60%}
		fraction {content:"\2044";vertical-align:middle;font-size:inherit}
		fraction:after {content:attr(denominator);vertical-align:bottom;font-size:60%}
	-->
	<xsl:template match="fraction">
		<span class="numerator"><xsl:value-of select="@numerator"/></span>
		<span class="fracslash"><xsl:text>&#x002f;</xsl:text></span>
		<span class="denominator"><xsl:value-of select="@denominator"/></span>
	</xsl:template>
	
	<!-- 
		lm
		If not first sibling, insert a comma.
		If @hom, prepend it.
		
		ls>lm+lm:before {content:", ";font-weight:bold}
		entry[crossref=true]>ls>lm[hom]:first-child:before {content:"\a"attr(hom)" ";font-weight:bold;white-space:pre}
		lm[hom]:before {content:attr(hom)" ";font-weight:bold}
		ls>lm+lm[hom]:before {content:", "attr(hom)" ";font-weight:bold}
	-->
	<xsl:template match="lm">
		<xsl:if test="preceding-sibling::*[1][self::lm]">
			<xsl:text>, </xsl:text>
		</xsl:if>
		<xsl:if test="@hom">
			<span class="hom"><xsl:value-of select="@hom"/></span>
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		ls
		
		UNTESTED
	
		sp>ls:first-child:before {content:"var. sp. of ";font-style:italic}
	-->
	<xsl:template match="ls[parent::sp and not(preceding-sibling::*)]">
		<span class="italic"><xsl:text>var. sp. of </xsl:text></span>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		note
	
		note:before {content:" {"}
		note:after {content:"} "}
	-->
	<xsl:template match="note">
		<xsl:text> </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:text>{</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>}</xsl:text>
		</xsl:copy>
		<xsl:text> </xsl:text>
	</xsl:template>
	
	<!-- 
		place, child of altplace
		Insert a comma between siblings.
		
		altplace>place+place:before {content:", "}
	-->
	<xsl:template match="place[parent::altplace]">
		<xsl:if test="preceding-sibling::*[1][self::place]">
			<xsl:text>, </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		sp
		
		UNTESTED
		
		sp:before {content:", ";font-style:normal}
	-->
	<xsl:template match="sp">
		<xsl:text>, </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		v, first child of sp
		Prepend "var. sp. of ".
		If @hom present, insert the value.
		
		sp>v:first-child:before {content:"var. sp. of ";font-style:italic}
		sp>v[hom]:first-child:before {content:"var. sp. of "attr(hom)" ";font-style:italic}
	-->
	<xsl:template match="v[parent::sp and not(preceding-sibling::*)]">
		<span class="italic"><xsl:text>var. sp. of </xsl:text></span>
		<xsl:if test="@hom">
			<xsl:value-of select="@hom"/>
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		v, child of see
		If previous sibling, insert comma and space.
		If @hom present, insert the value.
		If @senseref present, insert the value in parentheses.
		
		see>v+v:before {content:", "}
		see>v[hom]:before {content:attr(hom)" ";font-style:normal}
		see>v+v[hom]:before {content:", "attr(hom)" ";font-style:normal}
		see>v[senseref]:after {content:" ("attr(senseref)")"}
	-->
	<xsl:template match="v[parent::see]">
		<xsl:if test="preceding-sibling::*[1][self::v]">
			<xsl:text>, </xsl:text>
		</xsl:if>
		<xsl:if test="@hom">
			<xsl:value-of select="@hom"/>
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:if test="@senseref">
			<xsl:text>(</xsl:text>
			<xsl:value-of select="@senseref"/>
			<xsl:text>)</xsl:text>
		</xsl:if>
	</xsl:template>
	
	<!-- 
		type
		Surround with parentheses and following whitespace.
	
		type:before {content:"(";font-style:normal}
		type:after {content:") ";font-style:normal}
	-->
	<xsl:template match="type">
		<xsl:text>(</xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>) </xsl:text>
	</xsl:template>
	
	<!-- 
		v, child of ref
		No attempt to summarize – just look below.	
		
		Observations:
		It seems that @supinf assumes presence of @senseref.
		It seems that @supinf means element is empty.
		It seems that @hom and @senseref can appear together.
		The CSS doesn't seem entirely consistent here...
		
		/* xref for quotations */
		ref>v:before {content:" (v. "}
		ref>v:empty:before {content:""}
		qt>ref:only-child>v:only-child:before {content:" etc. (v. "}
		
		ref>v:after {content:")"}
		ref>v:empty:after {content:"[\2192]"}
		
		ref>v[hom]:before {content:" (v. "attr(hom)" "}
		
		ref>v[senseref]:empty:before {content:" (v. "}
		ref>v[senseref]:after {content:" "attr(senseref)")"}
		ref>v[senseref]:empty:after {content:attr(senseref)")"}
		
		ref>v[supinf]:after {content:attr(senseref)" "attr(supinf)")"}
		ref>v[supinf]:empty:after {content:attr(senseref)" "attr(supinf)")"}
	-->
	<xsl:template match="v[parent::ref]">
		<!--
			before
			In most cases, insert " (v. "
		-->
		<xsl:choose>
			<xsl:when test="not(node()|@senseref)">
			</xsl:when>
			<xsl:when test="parent::ref[count(*)=1 and parent::qt[count(*)=1]]">
				<xsl:text> etc. (v. </xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text> (v. </xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<!-- element and after -->
		<xsl:choose>
			<xsl:when test="@supinf">
				<xsl:value-of select="@senseref"/>
				<xsl:text> </xsl:text>
				<xsl:value-of select="@supinf"/>
				<xsl:text>)</xsl:text>
			</xsl:when>
			<xsl:when test="@senseref">
				<xsl:if test="@hom">
					<xsl:value-of select="@hom"/>
					<xsl:text> </xsl:text>
				</xsl:if>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:text> </xsl:text>
				<xsl:value-of select="@senseref"/>
				<xsl:text>)</xsl:text>
			</xsl:when>
			<xsl:when test="@hom">
				<xsl:value-of select="@hom"/>
				<xsl:text> </xsl:text>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:text>)</xsl:text>
			</xsl:when>
			<xsl:when test="not(node())">
				<!--<xsl:text>[&#x2192;]</xsl:text>-->
			</xsl:when>
			<xsl:otherwise>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:text>)</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- 
		v, child of 'def' or 'ed' or 'addinfo'
		
		# def>v is font-style:italic, but most reset to normal.
		def>v[hom]:before {content:attr(hom)" ";font-style:normal} #n
		def>v[supinf]:before {content:attr(senseref);font-style:normal} #n
		def>v[supinf]:after {content:" "attr(supinf);font-style:italic}
		def>v[senseref]:after {content:" "attr(senseref);font-style:normal} #n
		def>v[senseref]:empty:after {content:attr(senseref);font-style:normal} #n
		def>v[supinf]:empty:before {content:attr(senseref)" ";font-style:normal} #n
		def>v[supinf]:empty:after {content:attr(supinf);font-style:italic}

		# Same as def>v, but these are all font-style:normal.
		ed>v[hom]:before {content:attr(hom)" ";font-style:normal}
		ed>v[supinf]:before {content:attr(senseref);font-style:normal}
		ed>v[supinf]:after {content:" "attr(supinf);font-style:normal}
		ed>v[senseref]:after {content:" "attr(senseref);font-style:normal}
		ed>v[senseref]:empty:after {content:attr(senseref);font-style:normal}
		ed>v[supinf]:empty:before {content:attr(senseref)" ";font-style:normal}
		ed>v[supinf]:empty:after {content:attr(supinf);font-style:normal}
		
		# Exactly the same as def>v.
		addinfo>v[hom]:before {content:attr(hom)" ";font-style:normal} #n
		addinfo>v[supinf]:before {content:attr(senseref);font-style:normal} #n
		addinfo>v[supinf]:after {content:" "attr(supinf);font-style:italic}
		addinfo>v[senseref]:after {content:" "attr(senseref);font-style:normal} #n
		addinfo>v[senseref]:empty:after {content:attr(senseref);font-style:normal} #n
		addinfo>v[supinf]:empty:before {content:attr(senseref)" ";font-style:normal} #n
		addinfo>v[supinf]:empty:after {content:attr(supinf);font-style:italic}
	-->
	<xsl:template match="v[parent::def or parent::ed or parent::addinfo]">
		<xsl:choose>
			<xsl:when test="@supinf">
				<xsl:value-of select="@senseref"/>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:text> </xsl:text>
				<xsl:choose>
					<xsl:when test="parent::ed">
						<xsl:value-of select="@supinf"/>
					</xsl:when>
					<xsl:otherwise>
						<span class="italic"><xsl:value-of select="@supinf"/></span>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:when test="@senseref">
				<xsl:if test="@hom">
					<xsl:value-of select="@hom"/>
					<xsl:text> </xsl:text>
				</xsl:if>
				<xsl:if test="node()">
					<xsl:copy>
						<xsl:copy-of select="@*"/>
						<xsl:apply-templates/>
					</xsl:copy>
					<xsl:text> </xsl:text>					
				</xsl:if>
				<xsl:value-of select="@senseref"/>
			</xsl:when>
			<xsl:when test="@hom">
				<xsl:value-of select="@hom"/>
				<xsl:text> </xsl:text>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
			</xsl:when>
			<xsl:otherwise>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- 
		wk
		
		UNTESTED
		
		# def au+wk:before {content:" "}
		# type>au+wk:before {content:" "}
		
		Combined the rules to just:
		au+wk:before {content:" "}
	-->
	<xsl:template match="wk">
		<xsl:if test="preceding-sibling::*[1][self::au]">
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>

	<!-- 
		s1, without @snum
		Precede with a comma.
		
		s1:before {content:", "}
	-->
	<xsl:template match="s1[not(@snum)]">
		<xsl:text>, </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		s1, with @snum
		Insert the @snum value, style as "snum".
		
		s1[snum]:before {content:attr(snum) " ";font-weight:bold}
		# s1[snum]+s1[snum]:before {content:attr(snum) " ";font-weight:bold}
	-->
	<xsl:template match="s1[@snum]">
		<xsl:text> </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<span class="label"><xsl:value-of select="@snum"/></span>
			<xsl:text> </xsl:text>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		ref
		
		cf>*+ref:before {content:"; ";font-weight:normal}
		cf>ref+ref:before {content:", ";font-weight:normal}
		# cf>ref:last-child:after {content:""}
	-->
	<xsl:template match="ref[parent::cf]">
		<xsl:choose>
			<xsl:when test="preceding-sibling::*[1][self::ref]">
				<xsl:text>, </xsl:text>
			</xsl:when>
			<xsl:when test="preceding-sibling::*">
				<xsl:text>; </xsl:text>
			</xsl:when>
		</xsl:choose>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		s2
		If not first sibling, preced with em-space.
		
		s2+s2:before {content:"\2003"}
		# s2:after {content:""}
	-->
	<xsl:template match="s2">
		<xsl:if test="preceding-sibling::*[1][self::s2]">
			<xsl:text>&#x2003;</xsl:text>			
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		q2
		If not the first sibling, precede with two em spaces.
		If @let is present, show it and follow with en space.
		End with a period.
		
		q2:after {content:"."}
		q2+q2[let]:before {content:"\2003\2003" attr(let)"\2002";font-weight:bold}
		q2+q2:before {content:"\2003\2003";font-weight:bold}
		q2[let]:before {content:attr(let)"\2002";font-weight:bold}
	-->
	<xsl:template match="q2">
		<xsl:if test="preceding-sibling::*[1][self::q2]">
			<xsl:text>&#x2003;&#x2003;</xsl:text>
		</xsl:if>
		<xsl:if test="@let">
			<span class="label"><xsl:value-of select="@let"/></span>
			<xsl:text>&#x2002;</xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>.</xsl:text>
	</xsl:template>
	
	<!--
		qt
		Place semicolon between siblings.
		But if what came immediately before was an empty 'v', then use a comma.
		
		qt {}
		qt+qt:before {content:"; ";font-weight:normal}
	-->
	<xsl:template match="qt">
		<xsl:choose>
			<xsl:when test="preceding::*[1][self::v[not(@*|node())]]">
				<xsl:text>, </xsl:text>
			</xsl:when>
			<xsl:when test="preceding-sibling::*[1][self::qt]">
				<xsl:text>; </xsl:text>
			</xsl:when>
		</xsl:choose>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>

	<!--
		q
		Follow with a single space.
		
		q:after {content:" "}
		cf>q:after {content:""}
		cf>date+q:before {content:" "}
		cf>ref+q:before {content:": "}
		# cf>q+*:before {content:"; ";font-weight:normal} #handle elsewhere
	-->
	<xsl:template match="q">
		<xsl:choose>
			<xsl:when test="parent::cf and preceding-sibling::*[1][self::date]">
				<xsl:text> </xsl:text>
			</xsl:when>
			<xsl:when test="parent::cf and preceding-sibling::*[1][self::ref]">
				<xsl:text>: </xsl:text>
			</xsl:when>
		</xsl:choose>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:if test="not(parent::cf)">
			<xsl:text> </xsl:text>
		</xsl:if>
	</xsl:template>

	<!-- 
		au
		Follow with a space, unless last sibling.
		
		place au:after {content:" "}
		place au:last-child:after {content:""}
		au[pseud=true]:before {content:"Ps.-";font-style:italic;font-variant:normal}
	-->
	<xsl:template match="au">
		<!-- before -->
		<xsl:if test="@pseud='true'">
			<span class="pseud"><xsl:text>Ps.-</xsl:text></span>
		</xsl:if>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<xsl:if test="following-sibling::*">
			<xsl:text> </xsl:text>
		</xsl:if>
	</xsl:template>
	
	<!-- 
		loc
		
		UNTESTED
		
		wk+loc:before {content:" "}
		# type>wk+loc:before {content:" "}
		#! def au+loc:before {content:" "}
		#! type>au+loc:before {content:" "}
		
		Combined the ! rules to just:
		au+loc:before {content:" "}
	-->
	<xsl:template match="loc">
		<xsl:if test="preceding-sibling::*[1][self::wk or self::au]">
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- 
		cf
		
		cf:before {content:" (cf. "}
		cf:after {content:")"}
	-->
	<xsl:template match="cf">
		<xsl:text> (cf. </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>)</xsl:text>
	</xsl:template>
	
	<!--
		date
		
		TODO Check whether @recte and @type can coexist.

		# If parent is cf, don't add trailing space.
		date:after {content:" "}
		cf>date:after {content:""}
		date[recte]:after {content:" (recte "attr(recte)") ";font-weight:normal}
		cf>date[recte]:after {content:" (recte "attr(recte)")";font-weight:normal}

		date[type="sub"]:before {content:"s";font-weight:normal}
		date[type="post"]:before {content:"p";font-weight:normal}
		date[type="ante"]:before {content:"a";font-weight:normal}
		date[type="circa"]:before {content:"c";font-weight:normal}
		date[type="spurious"]:before {content:"\2020";font-weight:normal}
		date[type="query"]:before {content:"?\00a0";font-weight:normal}
		date[type="spurious-ante"]:before {content:"\2020\00a0a";font-weight:normal}
		date[type="spurious-post"]:before {content:"\2020\00a0p";font-weight:normal}
		date[type="spurious-circa"]:before {content:"\2020\00a0c";font-weight:normal}
		date[type="query-ante"]:before {content:"?\00a0a";font-weight:normal}
		date[type="query-post"]:before {content:"?\00a0p";font-weight:normal}
		date[type="query-circa"]:before {content:"?\00a0c";font-weight:normal}
		
		# Same as regular 'date' handling! No action needed for these.
		cf>date[type="sub"]:before {content:"s";font-weight:normal}
		cf>date[type="post"]:before {content:"p";font-weight:normal}
		cf>date[type="ante"]:before {content:"a";font-weight:normal}
		cf>date[type="circa"]:before {content:"c";font-weight:normal}
		cf>date[type="spurious"]:before {content:"\2020";font-weight:normal}
		cf>date[type="spurious-ante"]:before {content:"\2020\00a0a";font-weight:normal}
		cf>date[type="spurious-post"]:before {content:"\2020\00a0p";font-weight:normal}
		cf>date[type="spurious-circa"]:before {content:"\2020\00a0c";font-weight:normal}
		cf>date[type="query"]:before {content:"?\00a0";font-weight:normal}
		cf>date[type="query-ante"]:before {content:"?\00a0a";font-weight:normal}
		cf>date[type="query-post"]:before {content:"?\00a0p";font-weight:normal}
		cf>date[type="query-circa"]:before {content:"?\00a0c";font-weight:normal}

		# Same as regular 'date', but prepend all with ": ".
		cf>ref+date:before {content:": ";font-weight:normal}
		cf>ref+date[type="sub"]:before {content:": s";font-weight:normal}
		cf>ref+date[type="post"]:before {content:": p";font-weight:normal}
		cf>ref+date[type="ante"]:before {content:": a";font-weight:normal}
		cf>ref+date[type="circa"]:before {content:": c";font-weight:normal}
		cf>ref+date[type="spurious"]:before {content:": \2020";font-weight:normal}
		cf>ref+date[type="spurious-ante"]:before {content:": \2020\00a0a";font-weight:normal}
		cf>ref+date[type="spurious-post"]:before {content:": \2020\00a0p";font-weight:normal}
		cf>ref+date[type="spurious-circa"]:before {content:": \2020\00a0c";font-weight:normal}
		cf>ref+date[type="query"]:before {content:": ?\00a0";font-weight:normal}
		cf>ref+date[type="query-ante"]:before {content:": ?\00a0a";font-weight:normal}
		cf>ref+date[type="query-post"]:before {content:": ?\00a0p";font-weight:normal}
		cf>ref+date[type="query-circa"]:before {content:": ?\00a0c";font-weight:normal}
	-->
	<xsl:template match="date">
		<!-- before -->
		<xsl:if test="parent::cf and preceding-sibling::*[1][self::ref]">
			<xsl:text>: </xsl:text>
		</xsl:if>
		<!-- date prefix -->
		<xsl:choose>
			<xsl:when test="@type='sub'">
				<xsl:text>s</xsl:text>
			</xsl:when>
			<xsl:when test="@type='post'">
				<xsl:text>p</xsl:text>
			</xsl:when>
			<xsl:when test="@type='ante'">
				<xsl:text>a</xsl:text>
			</xsl:when>
			<xsl:when test="@type='circa'">
				<xsl:text>c</xsl:text>
			</xsl:when>
			<xsl:when test="@type='spurious'">
				<xsl:text>&#x2020;</xsl:text>
			</xsl:when>
			<xsl:when test="@type='spurious-ante'">
				<xsl:text>&#x2020;&#x00a0;a</xsl:text>
			</xsl:when>
			<xsl:when test="@type='spurious-post'">
				<xsl:text>&#x2020;&#x00a0;p</xsl:text>
			</xsl:when>
			<xsl:when test="@type='spurious-circa'">
				<xsl:text>&#x2020;&#x00a0;c</xsl:text>
			</xsl:when>
			<xsl:when test="@type='query'">
				<xsl:text>?&#x00a0;</xsl:text>
			</xsl:when>
			<xsl:when test="@type='query-ante'">
				<xsl:text>?&#x00a0;a</xsl:text>
			</xsl:when>
			<xsl:when test="@type='query-post'">
				<xsl:text>?&#x00a0;p</xsl:text>
			</xsl:when>
			<xsl:when test="@type='query-circa'">
				<xsl:text>?&#x00a0;c</xsl:text>
			</xsl:when>
		</xsl:choose>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- additional -->
		<xsl:if test="@recte">
			<xsl:text> (</xsl:text>
			<xsl:value-of select="@recte"/>
			<xsl:text>)</xsl:text>
		</xsl:if>
		<!-- after -->
		<xsl:choose>
			<xsl:when test="following-sibling::*[1][self::ref[*[1][self::v[not(@*|node())]]]]">
				<!-- Followed immediately by a ref, whose first element is an empty v.
					Do not append a trailing space. See 'salsus2'. -->
			</xsl:when>
			<xsl:when test="parent::cf">
			</xsl:when>
			<xsl:otherwise>
				<xsl:text> </xsl:text>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- 
		def
	
		# s1>def:before {content:""}
		s1>def:after {content:": "}
		# s2>def:before {content:""}
		# s2>def:first-child:before {content:""}
		s2>def[let]:before {content:attr(let)"\2002";font-weight:bold}
		# s2>def[let]:first-child:before {content:attr(let)"\2002";font-weight:bold}
		s2>def:after {content:"; "}
		s2>def:last-child:after {content:"."}
		# v+s1>s2>def:first-child:before {content:""}
	-->
	<xsl:template match="def[parent::s1 or parent::s2]">
		<xsl:choose>
			<xsl:when test="parent::s1">
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:text>: </xsl:text>
			</xsl:when>
			<xsl:when test="parent::s2">
				<xsl:if test="@let">
					<span class="label"><xsl:value-of select="@let"/></span>
					<xsl:text>&#x2002;</xsl:text>
				</xsl:if>
				<xsl:copy>
					<xsl:copy-of select="@*"/>
					<xsl:apply-templates/>
				</xsl:copy>
				<xsl:if test="position()=last()">
					<xsl:text>.</xsl:text>
				</xsl:if>
				<xsl:if test="position() &lt; last()">
					<xsl:text>; </xsl:text>
				</xsl:if>
			</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<!--
		dub
	
		dub:before {content:"dub."}
	-->
	<xsl:template match="dub">
		<xsl:text>dub.</xsl:text>
	</xsl:template>
	
	<!-- 
		e
		
		Assume that @attest and @hom cannot appear together. 
	
		e[lang]:before {content:attr(lang)" ";font-style:normal}
		e[lang]:empty:before {content:attr(lang);font-style:normal}
		e[lang][attest="false"]:before {content:attr(lang)" *";font-style:normal}

		e[attest="false"]:not([lang]):before {content:"*";font-style:normal}
		e[hom]:not([lang]):before {content:attr(hom)" ";font-style:normal}
		# e:not([lang]):before {content:""}
	-->
	<xsl:template match="e">
		<xsl:choose>
			<xsl:when test="@lang and @attest='false'">
				<xsl:value-of select="@lang"/>
				<xsl:text> *</xsl:text>
			</xsl:when>
			<xsl:when test="@lang">
				<xsl:value-of select="@lang"/>
				<xsl:if test="node()">
					<xsl:text> </xsl:text>
				</xsl:if>
			</xsl:when>
			<xsl:when test="not(@lang) and @hom">
				<xsl:value-of select="@hom"/>
				<xsl:text> </xsl:text>
			</xsl:when>
			<xsl:when test="not(@lang) and @attest='false'">
				<xsl:text>*</xsl:text>
			</xsl:when>
		</xsl:choose>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		ed
		Surround with brackets.
		
		ed:before {content:"["}
		ed:after {content:"]"} 
	-->
	<xsl:template match="ed">
		<xsl:text>[</xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>]</xsl:text>
	</xsl:template>
	
	<!--
		id
		Insert text "Id." (italicized),
		but if within "cf" or "ed", insert text "id." (normal).
		Add a following space, unless last sibling.
		
		id:before {content:"Id. "; text-decoration:none;font-weight:normal;font-style:italic}
		cf>ref>place>id:before {content:"id. "; text-decoration:none;font-weight:normal;font-style:normal}
		cf>ref>place>id:last-child:before {content:"id."; text-decoration:none;font-weight:normal;font-style:normal}
		ed>place>id:before {content:"id. "; text-decoration:none;font-weight:normal;font-style:normal}
	-->
	<xsl:template match="id">
		<xsl:choose>
			<xsl:when test="ancestor::cf or ancestor::ed">
				<span class="little-id"><xsl:text>id.</xsl:text></span>
			</xsl:when>
			<xsl:otherwise>
				<span class="big-id"><xsl:text>Id.</xsl:text></span>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:if test="following-sibling::*">
			<xsl:text> </xsl:text>
		</xsl:if>
	</xsl:template>
	
	<!-- 
		ibid
		The CSS rules are a bit different from 'id', but basically treat it the same. 
		
		ibid:before {content:"Ib. ";font-style:italic}
		q2>qt:last-child>ref:last-child>place:last-child>ibid:last-child:before {content:"Ib";font-style:italic}
		place>ibid:last-child:before {content:"Ib.";font-style:italic}
		cf>ref>place>ibid:before {content:"ib. ";font-style:normal}
		ed>place>ibid:before {content:"ib. ";font-style:normal}
		cf>ref>place>ibid:last-child:before {content:"ib.";font-style:normal}
	-->
	<xsl:template match="ibid">
		<xsl:choose>
			<xsl:when test="ancestor::cf or ancestor::ed">
				<span class="little-ibid"><xsl:text>ib.</xsl:text></span>
			</xsl:when>
			<xsl:otherwise>
				<span class="big-ibid"><xsl:text>Ib.</xsl:text></span>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:if test="following-sibling::*">
			<xsl:text> </xsl:text>
		</xsl:if>
	</xsl:template>
	
	<!-- 
		insp
		
		insp:before {content:"("}
		insp:after {content:") "}
		cf>q+insp:before {content:"; (";font-weight:normal}
		cf>date+insp:before {content:" ("}
		cf>ref+insp:before {content:": ("}
	-->
	<xsl:template match="insp">
		<!-- before -->
		<xsl:choose>
			<xsl:when test="parent::cf and preceding-sibling::*[1][self::q]">
				<xsl:text>; (</xsl:text>
			</xsl:when>
			<xsl:when test="parent::cf and preceding-sibling::*[1][self::date]">
				<xsl:text> (</xsl:text>
			</xsl:when>
			<xsl:when test="parent::cf and preceding-sibling::*[1][self::ref]">
				<xsl:text>: (</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>(</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<xsl:text>) </xsl:text>
	</xsl:template>
	
	<!--
		l
		
		l[fl=true]:before {content:"\2020";font-weight:normal}
		l[alt]:after {content:" ("attr(alt)")";font-weight:bold}
	-->
	<xsl:template match="l">
		<!-- before -->
		<xsl:if test="@fl='true'">
			<xsl:text>&#x2020;</xsl:text>
		</xsl:if>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<xsl:if test="@alt">
			<span class="lemmaalt"><xsl:text> (</xsl:text>
			<xsl:value-of select="@alt"/>
			<xsl:text>)</xsl:text></span>
		</xsl:if>
	</xsl:template>
	
	<!-- 
		see
	
		entry[crossref=true]>see:after {content:"."}
		/* For cross ref entries*/
		entry>see:before {content:" v. "}
		entry>see[also=true]:before {content:" v. et. "}
	-->
	<xsl:template match="see">
		<!-- before -->
		<xsl:choose>
			<xsl:when test="@also='true'">
				<xsl:text> v. et. </xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text> v. </xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<!-- element -->
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<!-- after -->
		<xsl:if test="parent::entry[@crossref='true']">
			<xsl:text>.</xsl:text>			
		</xsl:if>
	</xsl:template>
	
	<!-- 
		vern
	
		ed>vern[lang]:before {content:attr(lang)": ";font-style:normal}
	-->
	<xsl:template match="vern[parent::ed and @lang]">
		<xsl:value-of select="@lang"/>
		<xsl:text>: </xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!--
		q1
		
		Not necessary to do this, but pad with whitespace.
	-->
	<xsl:template match="q1">
		<xsl:text>
</xsl:text>
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
		<xsl:text>
</xsl:text>
	</xsl:template>
	
	<!-- 
		Any vertical bars that appear within a 'q' element (including children)
		should be replaced with a slash.
	-->
	<xsl:template match="text()[ancestor::q and contains(., '|')]">
		<xsl:value-of select="replace(., '\|', '/')"/>
	</xsl:template>
	
	<!--
		Copy out everything else, without modifications.
	-->
	<xsl:template match="@*|node()" mode="#all" priority="-1">
		<xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
	</xsl:template>
	
</xsl:stylesheet>
