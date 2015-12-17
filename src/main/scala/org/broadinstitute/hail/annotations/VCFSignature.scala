package org.broadinstitute.hail.annotations

import htsjdk.variant.vcf.{VCFInfoHeaderLine, VCFHeaderLineCount, VCFHeaderLineType}

case class VCFSignature(vcfType: String, emitType: String, number: String,
  emitConversionIdentifier: String, description: String)
  extends AnnotationSignature {

  def this(scalaType: String, conversionMethod: String, desc: String) =
    this("", scalaType, "", conversionMethod, "")

  def emitUtilities: String = ""
}

object VCFSignature {

  val arrayRegex = """Array\[(\w+)\]""".r
  val setRegex = """Set\[(\w+)\]""".r

  def getConversionMethod(str: String): String = {
    str match {
      case arrayRegex(subType) => s"toArray$subType"
      case setRegex(subType) => s"toSet$subType"
      case _ => s"to$str"
    }
  }

  def vcfTypeToScala(str: String): String =
    str match {
      case "Flag" => "Boolean"
      case "Integer" => "Int"
      case "Float" => "Double"
      case "String" => "String"
      case "Character" => "Character"
      case "." => "String"
      case _ => throw new UnsupportedOperationException("unexpected annotation type")
    }

  val integerRegex = """(\d+)""".r

  def parse(line: VCFInfoHeaderLine): AnnotationSignature = {
    val vcfType = line.getType.toString
    val parsedType = line.getType match {
      case VCFHeaderLineType.Integer => "Int"
      case VCFHeaderLineType.Float => "Double"
      case VCFHeaderLineType.String => "String"
      case VCFHeaderLineType.Character => "Character"
      case VCFHeaderLineType.Flag => "Boolean"
    }
    val parsedCount = line.getCountType match {
      case VCFHeaderLineCount.A => "A"
      case VCFHeaderLineCount.G => "G"
      case VCFHeaderLineCount.R => "R"
      case VCFHeaderLineCount.INTEGER => line.getCount.toString
      case VCFHeaderLineCount.UNBOUNDED => "."
    }
    val scalaType = parsedCount match {
      case "A" | "R" | "G" => s"Array[$parsedType]"
      case integerRegex(i) => if (i.toInt > 1) s"Array[$parsedType]" else parsedType
      case _ => parsedType
    }
    val conversionMethod = getConversionMethod(scalaType)
    val desc = line.getDescription


    new VCFSignature(vcfType, scalaType, parsedCount, conversionMethod, desc)


  }
}
