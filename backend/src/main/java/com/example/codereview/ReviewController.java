package com.example.codereview;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/review")
public class ReviewController {
  private final CodeReviewService service;
  public ReviewController(CodeReviewService service){ this.service = service; }
  @PostMapping
  public Map<String,Object> review(@RequestBody Map<String,String> body){
    String code = body.get("code");
    return service.reviewCode(code == null ? "" : code);
  }
}