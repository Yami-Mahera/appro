using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ModularWebAPI.Auth.Do
{
    public class LigneCommande
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        public Guid CommandeId { get; set; }
        
        [Required]
        public Guid ArticleId { get; set; }
        
        [Required]
        public int Quantite { get; set; }
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal PrixUnitaire { get; set; }
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal Total { get; set; }
    }
}