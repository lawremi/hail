package org.broadinstitute.k3.methods

import org.broadinstitute.k3.variant._

object nHomRefPerVariant extends VariantMethod[Int] {
  def name = "nHomRef"

  def apply(vds: VariantDataset): Map[Variant, Int] = {
    vds
      .mapValues(g => if (g.isHomRef) 1 else 0)
      .reduceByVariant(_ + _)
  }
}
